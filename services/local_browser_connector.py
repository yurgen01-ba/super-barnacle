from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse
from urllib.request import urlopen
from uuid import uuid4

from memory.db import get_connection
from repositories.memory_repository import MemoryRepository
from repositories.source_repository import SourceRepository
from repositories.workspace_repository import workspace_repository
from services.atlassian_sync_service import AtlassianSyncService, _html_text
from services.participant_extraction_service import extract_participants_from_text


class LocalBrowserConnectorError(RuntimeError):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def validate_start_url(value: str) -> str:
    url = str(value or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Enter a complete http:// or https:// address")
    if parsed.username or parsed.password:
        raise ValueError("Do not put a login or password in the address")
    return url


def _browser_executable() -> str:
    configured = os.getenv("PROJECT_BRAIN_BROWSER_EXECUTABLE", "").strip()
    candidates = [
        configured,
        shutil.which("chrome") or "",
        shutil.which("chrome.exe") or "",
        shutil.which("msedge") or "",
        shutil.which("msedge.exe") or "",
        str(Path(os.getenv("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe"),
        str(Path(os.getenv("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe"),
        str(Path(os.getenv("PROGRAMFILES", "")) / "Microsoft/Edge/Application/msedge.exe"),
        str(Path(os.getenv("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise LocalBrowserConnectorError(
        "Chrome or Microsoft Edge was not found. Set PROJECT_BRAIN_BROWSER_EXECUTABLE."
    )


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@dataclass
class LocalBrowserSession:
    id: str
    user_id: str
    project_id: str
    provider: str
    start_url: str
    profile_dir: str
    port: int
    process: subprocess.Popen
    created_at: datetime = field(default_factory=_utcnow)
    busy: bool = False

    def public(self) -> dict:
        return {
            "id": self.id,
            "provider": self.provider,
            "start_url": self.start_url,
            "created_at": self.created_at.isoformat(),
            "busy": self.busy,
            "running": self.process.poll() is None,
        }


class LocalBrowserSessionRegistry:
    """Process-local registry for visible, disposable browser sessions."""

    def __init__(self):
        self._sessions: dict[str, LocalBrowserSession] = {}
        self._lock = threading.RLock()

    def start(self, *, user_id: str, project_id: str, provider: str, start_url: str) -> dict:
        provider = str(provider or "").lower()
        if provider not in {"atlassian", "slack"}:
            raise ValueError("Unsupported browser connector")
        start_url = validate_start_url(start_url)
        self.close_for(user_id=user_id, project_id=project_id, provider=provider)
        profile_dir = tempfile.mkdtemp(prefix=f"project_brain_{provider}_")
        port = _free_local_port()
        executable = _browser_executable()
        args = [
            executable,
            f"--remote-debugging-port={port}",
            "--remote-debugging-address=127.0.0.1",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-sync",
            "--disable-save-password-bubble",
            "--disable-features=PasswordManagerOnboarding,AutofillServerCommunication",
            "--new-window",
            start_url,
        ]
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        process = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        session = LocalBrowserSession(
            id=str(uuid4()), user_id=user_id, project_id=project_id,
            provider=provider, start_url=start_url, profile_dir=profile_dir,
            port=port, process=process,
        )
        with self._lock:
            self._sessions[session.id] = session
        try:
            self._wait_until_ready(session)
        except Exception:
            self.close(session.id, user_id=user_id, project_id=project_id)
            raise
        return session.public()

    @staticmethod
    def _wait_until_ready(session: LocalBrowserSession, timeout: float = 15.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if session.process.poll() is not None:
                raise LocalBrowserConnectorError("The local browser closed before it was ready")
            try:
                with urlopen(f"http://127.0.0.1:{session.port}/json/version", timeout=1):
                    return
            except OSError:
                time.sleep(0.2)
        raise LocalBrowserConnectorError("The local browser did not become ready")

    def require(
        self, session_id: str, *, user_id: str, project_id: str, provider: str | None = None
    ) -> LocalBrowserSession:
        with self._lock:
            session = self._sessions.get(str(session_id or ""))
        if not session or session.user_id != user_id or session.project_id != project_id:
            raise LocalBrowserConnectorError("This browser session is unavailable")
        if provider and session.provider != provider:
            raise LocalBrowserConnectorError("The browser session belongs to another connector")
        if session.process.poll() is not None:
            self.close(session.id, user_id=user_id, project_id=project_id)
            raise LocalBrowserConnectorError("The local browser was closed")
        return session

    def find(self, *, user_id: str, project_id: str, provider: str) -> dict | None:
        with self._lock:
            sessions = list(self._sessions.values())
        for session in sessions:
            if (
                session.user_id == user_id and session.project_id == project_id
                and session.provider == provider and session.process.poll() is None
            ):
                return {**session.public(), **self.status(session)}
        return None

    @staticmethod
    def status(session: LocalBrowserSession) -> dict:
        try:
            with urlopen(f"http://127.0.0.1:{session.port}/json", timeout=2) as response:
                tabs = json.loads(response.read().decode("utf-8"))
        except Exception:
            tabs = []
        pages = [
            {"title": str(tab.get("title", "")), "url": str(tab.get("url", ""))}
            for tab in tabs if tab.get("type") == "page" and str(tab.get("url", "")).startswith("http")
        ]
        return {"pages": pages, "ready": bool(pages)}

    def set_busy(self, session_id: str, value: bool) -> None:
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].busy = bool(value)

    def claim(
        self, session_id: str, *, user_id: str, project_id: str, provider: str
    ) -> LocalBrowserSession:
        with self._lock:
            session = self.require(
                session_id, user_id=user_id, project_id=project_id, provider=provider
            )
            if session.busy:
                raise LocalBrowserConnectorError("This browser session is already being imported")
            session.busy = True
            return session

    def close_for(self, *, user_id: str, project_id: str, provider: str) -> None:
        with self._lock:
            ids = [
                item.id for item in self._sessions.values()
                if item.user_id == user_id and item.project_id == project_id
                and item.provider == provider
            ]
        for session_id in ids:
            self.close(session_id, user_id=user_id, project_id=project_id)

    def close(self, session_id: str, *, user_id: str, project_id: str) -> None:
        with self._lock:
            session = self._sessions.get(str(session_id or ""))
            if not session or session.user_id != user_id or session.project_id != project_id:
                return
            self._sessions.pop(session.id, None)
        if session.process.poll() is None:
            try:
                session.process.terminate()
                session.process.wait(timeout=4)
            except Exception:
                try:
                    session.process.kill()
                except Exception:
                    pass
        for _ in range(8):
            try:
                shutil.rmtree(session.profile_dir)
                break
            except OSError:
                time.sleep(0.25)


class LocalBrowserConnectorService:
    def __init__(self, registry: LocalBrowserSessionRegistry | None = None):
        self.registry = registry or local_browser_session_registry
        self.max_items = max(100, int(os.getenv("LOCAL_BROWSER_CONNECTOR_MAX_ITEMS", "5000")))

    @staticmethod
    def _playwright():
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise LocalBrowserConnectorError(
                "Install the Playwright Python package to use the local browser connector"
            ) from exc
        return sync_playwright

    def sync(
        self, *, session_id: str, user_id: str, project_id: str,
        provider: str, sync_jira: bool = True, sync_confluence: bool = True,
        progress=None,
    ) -> dict:
        session = self.registry.claim(
            session_id, user_id=user_id, project_id=project_id, provider=provider
        )
        try:
            sync_playwright = self._playwright()
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(
                    f"http://127.0.0.1:{session.port}", timeout=15_000
                )
                context = browser.contexts[0]
                if provider == "atlassian":
                    result = self._sync_atlassian(
                        context, session.start_url, project_id,
                        sync_jira=sync_jira, sync_confluence=sync_confluence,
                        progress=progress,
                    )
                else:
                    result = self._sync_slack(context, session.start_url, project_id, progress)
            workspace_repository.log_event(
                project_id, "source", "Local browser synchronization completed",
                {"provider": provider, **result},
            )
            return result
        finally:
            self.registry.close(session.id, user_id=user_id, project_id=project_id)

    @staticmethod
    def _page_for_provider(context, start_url: str, provider: str):
        start = urlparse(start_url)
        fallback_origin = f"{start.scheme}://{start.netloc}"
        product_pages = []
        for page in reversed(context.pages):
            parsed = urlparse(page.url)
            if parsed.scheme not in {"http", "https"}:
                continue
            hostname = (parsed.hostname or "").lower()
            path = parsed.path.lower()
            if provider == "slack" and (
                hostname == "app.slack.com" or "/client/" in path
            ):
                product_pages.append(page)
            elif provider == "atlassian" and (
                hostname.endswith(".atlassian.net")
                or "/jira" in path or "/wiki" in path
            ) and hostname not in {"id.atlassian.com", "auth.atlassian.com"}:
                product_pages.append(page)
        if product_pages:
            page = product_pages[0]
            parsed = urlparse(page.url)
            return page, f"{parsed.scheme}://{parsed.netloc}"
        for page in reversed(context.pages):
            if page.url.startswith(fallback_origin):
                return page, fallback_origin
        page = context.new_page()
        page.goto(start_url, wait_until="domcontentloaded", timeout=45_000)
        return page, fallback_origin

    @staticmethod
    def _fetch_json(page, url: str) -> tuple[int, dict | list | None, str]:
        response = page.evaluate(
            """async (url) => {
                const response = await fetch(url, {
                    method: 'GET', credentials: 'include',
                    headers: {'Accept': 'application/json'}
                });
                const text = await response.text();
                return {status: response.status, text, finalUrl: response.url};
            }""",
            url,
        )
        text = str(response.get("text", ""))
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = None
        return int(response.get("status", 0)), payload, text[:500]

    def _sync_atlassian(
        self, context, start_url: str, project_id: str, *,
        sync_jira: bool, sync_confluence: bool, progress=None,
    ) -> dict:
        page, origin = self._page_for_provider(context, start_url, "atlassian")
        result = {"site": origin, "jira": {}, "confluence": {}}
        if sync_jira:
            if progress:
                progress(0.04, "browser:jira", "Reading Jira through the signed-in browser")
            result["jira"] = self._browser_jira(page, origin, project_id, progress)
        if sync_confluence:
            if progress:
                progress(0.52, "browser:confluence", "Reading Confluence through the signed-in browser")
            result["confluence"] = self._browser_confluence(page, origin, project_id, progress)
        if progress:
            progress(1.0, "completed", "Local Atlassian import completed")
        return result

    def _browser_jira(self, page, origin: str, project_id: str, progress=None) -> dict:
        candidates = [
            ("v3", f"{origin}/rest/api/3/search/jql"),
            ("v2", f"{origin}/rest/api/2/search"),
        ]
        issues: list[dict] = []
        errors: list[str] = []
        working: tuple[str, str] | None = None
        for api_version, endpoint in candidates:
            query = quote("ORDER BY updated ASC")
            status, payload, preview = self._fetch_json(
                page, f"{endpoint}?jql={query}&maxResults=100&fields=*all"
            )
            if status == 200 and isinstance(payload, dict) and "issues" in payload:
                working = (api_version, endpoint)
                issues.extend(payload.get("issues", []))
                break
            errors.append(f"{api_version}: HTTP {status} {preview[:120]}")
        if not working:
            return {"found": 0, "saved": 0, "errors": errors, "available": False}

        api_version, endpoint = working
        start_at = len(issues)
        total = int((payload or {}).get("total", len(issues)))
        next_token = (payload or {}).get("nextPageToken")
        while len(issues) < min(total, self.max_items):
            query = quote("ORDER BY updated ASC")
            suffix = f"&startAt={start_at}" if api_version == "v2" else (
                f"&nextPageToken={quote(str(next_token))}" if next_token else ""
            )
            status, page_payload, preview = self._fetch_json(
                page, f"{endpoint}?jql={query}&maxResults=100&fields=*all{suffix}"
            )
            if status != 200 or not isinstance(page_payload, dict):
                errors.append(f"page {start_at}: HTTP {status} {preview[:120]}")
                break
            batch = page_payload.get("issues", [])
            if not batch:
                break
            issues.extend(batch)
            start_at += len(batch)
            next_token = page_payload.get("nextPageToken")
            if api_version == "v3" and not next_token:
                break

        saved = 0
        for index, issue in enumerate(issues[: self.max_items], start=1):
            key = str(issue.get("key") or issue.get("id") or index)
            detail_url = f"{origin}/rest/api/{'3' if api_version == 'v3' else '2'}/issue/{quote(key)}?fields=*all&expand=changelog,renderedFields"
            status, detail, _ = self._fetch_json(page, detail_url)
            if status == 200 and isinstance(detail, dict):
                issue = detail
            text = AtlassianSyncService._jira_issue_text(issue)
            AtlassianSyncService._save_document(
                project_id=project_id,
                name=f"{key}: {(issue.get('fields') or {}).get('summary', '')}",
                source_type="browser_jira", source_ref=f"{origin}|{key}", text=text,
                item_type="jira_issue", item_title=f"{key}: {(issue.get('fields') or {}).get('summary', '')}",
            )
            saved += 1
            if progress and issues:
                progress(0.05 + 0.43 * index / len(issues), "browser:jira", f"Jira {index}/{len(issues)}")
        return {"found": len(issues), "saved": saved, "errors": errors, "available": True}

    def _browser_confluence(self, page, origin: str, project_id: str, progress=None) -> dict:
        candidates = [
            ("v2", f"{origin}/wiki/api/v2/pages?limit=100&body-format=storage"),
            ("v1wiki", f"{origin}/wiki/rest/api/content?type=page&limit=100&expand=body.storage,version,space,history,ancestors"),
            ("v1", f"{origin}/rest/api/content?type=page&limit=100&expand=body.storage,version,space,history,ancestors"),
        ]
        pages: list[dict] = []
        errors: list[str] = []
        working: tuple[str, str] | None = None
        payload: dict | None = None
        for api_version, endpoint in candidates:
            status, candidate_payload, preview = self._fetch_json(page, endpoint)
            if status == 200 and isinstance(candidate_payload, dict) and "results" in candidate_payload:
                working = (api_version, endpoint)
                payload = candidate_payload
                pages.extend(candidate_payload.get("results", []))
                break
            errors.append(f"{api_version}: HTTP {status} {preview[:120]}")
        if not working:
            return {"found": 0, "saved": 0, "errors": errors, "available": False}

        api_version, endpoint = working
        while len(pages) < self.max_items:
            next_url = ((payload or {}).get("_links") or {}).get("next")
            if not next_url:
                break
            status, payload, preview = self._fetch_json(page, urljoin(origin, next_url))
            if status != 200 or not isinstance(payload, dict):
                errors.append(f"next: HTTP {status} {preview[:120]}")
                break
            batch = payload.get("results", [])
            if not batch:
                break
            pages.extend(batch)

        saved = 0
        for index, item in enumerate(pages[: self.max_items], start=1):
            content_id = str(item.get("id") or index)
            detail = item
            body = item.get("body") or {}
            if not body:
                if api_version == "v2":
                    detail_url = f"{origin}/wiki/api/v2/pages/{quote(content_id)}?body-format=storage"
                else:
                    prefix = "/wiki" if api_version == "v1wiki" else ""
                    detail_url = f"{origin}{prefix}/rest/api/content/{quote(content_id)}?expand=body.storage,version,space,history,ancestors"
                status, candidate_detail, _ = self._fetch_json(page, detail_url)
                if status == 200 and isinstance(candidate_detail, dict):
                    detail = candidate_detail
            text = self._confluence_browser_text(detail)
            title = str(detail.get("title") or f"Confluence {content_id}")
            AtlassianSyncService._save_document(
                project_id=project_id, name=title,
                source_type="browser_confluence", source_ref=f"{origin}|{content_id}",
                text=text, item_type="confluence_page", item_title=title,
            )
            saved += 1
            if progress and pages:
                progress(0.53 + 0.45 * index / len(pages), "browser:confluence", f"Confluence {index}/{len(pages)}")
        return {"found": len(pages), "saved": saved, "errors": errors, "available": True}

    @staticmethod
    def _confluence_browser_text(item: dict) -> str:
        body = item.get("body") or {}
        storage = body.get("storage", body) if isinstance(body, dict) else {}
        value = storage.get("value", "") if isinstance(storage, dict) else str(storage)
        space = item.get("space") or {}
        version = item.get("version") or {}
        history = item.get("history") or {}
        return "\n".join([
            f"Title: {item.get('title', '')}",
            f"Status: {item.get('status', '')}",
            f"Space: {space.get('name', '') if isinstance(space, dict) else space}",
            f"Version: {version.get('number', '') if isinstance(version, dict) else version}",
            f"Created: {item.get('createdAt', '') or (history.get('createdDate', '') if isinstance(history, dict) else '')}",
            "", _html_text(value),
        ]).strip()

    def _sync_slack(self, context, start_url: str, project_id: str, progress=None) -> dict:
        page, origin = self._page_for_provider(context, start_url, "slack")
        page.wait_for_timeout(1500)
        hrefs = page.locator('a[href*="/client/"]').evaluate_all(
            "els => els.map(el => ({href: el.href, text: (el.innerText || el.textContent || '').trim()}))"
        )
        links = self.slack_conversation_links(hrefs, origin)[: min(self.max_items, 250)]
        if not links:
            raise LocalBrowserConnectorError(
                "No Slack conversations are visible. Open the workspace and wait for the sidebar to load."
            )
        saved = 0
        message_count = 0
        errors: list[str] = []
        for index, link in enumerate(links, start=1):
            try:
                page.goto(link["href"], wait_until="domcontentloaded", timeout=45_000)
                page.wait_for_timeout(1800)
                messages = self._collect_slack_messages(page)
                if not messages:
                    continue
                title = link["text"] or link["conversation_id"]
                text = "\n\n".join(messages)
                self._save_slack_document(
                    project_id=project_id, title=title,
                    source_ref=f"{origin}|{link['conversation_id']}", text=text,
                )
                saved += 1
                message_count += len(messages)
            except Exception as exc:
                errors.append(f"{link['conversation_id']}: {type(exc).__name__}: {exc}")
            if progress and links:
                progress(0.05 + 0.93 * index / len(links), "browser:slack", f"Slack {index}/{len(links)}")
        if progress:
            progress(1.0, "completed", "Local Slack import completed")
        return {
            "workspace": origin, "conversations_found": len(links),
            "conversations_saved": saved, "messages_saved": message_count,
            "errors": errors,
        }

    @staticmethod
    def slack_conversation_links(items: list[dict], origin: str) -> list[dict]:
        found: dict[str, dict] = {}
        pattern = re.compile(r"/client/[^/]+/([A-Z][A-Z0-9]+)(?:/|$)")
        for item in items:
            href = str(item.get("href", ""))
            if not href.startswith(origin):
                continue
            match = pattern.search(urlparse(href).path)
            if not match:
                continue
            conversation_id = match.group(1)
            found.setdefault(conversation_id, {
                "conversation_id": conversation_id,
                "href": href.split("?", 1)[0],
                "text": str(item.get("text", "")).strip().lstrip("#").strip(),
            })
        return list(found.values())

    @staticmethod
    def _collect_slack_messages(page, max_rounds: int = 80) -> list[str]:
        script = """() => {
            const selectors = [
                '[data-qa="message_container"]',
                '[data-qa^="message_container"]',
                '.c-virtual_list__item[role="listitem"]'
            ];
            let nodes = [];
            for (const selector of selectors) {
                nodes = Array.from(document.querySelectorAll(selector));
                if (nodes.length) break;
            }
            const messages = nodes.map(node => (node.innerText || '').trim()).filter(Boolean);
            const scrollables = Array.from(document.querySelectorAll('*')).filter(el =>
                el.scrollHeight > el.clientHeight + 300 && el.clientHeight > 300
            ).sort((a, b) => b.scrollHeight - a.scrollHeight);
            const pane = scrollables[0];
            if (pane) pane.scrollTop = Math.max(0, pane.scrollTop - Math.max(500, pane.clientHeight * .85));
            return {messages, scrollTop: pane ? pane.scrollTop : 0};
        }"""
        seen: dict[str, str] = {}
        unchanged = 0
        for _ in range(max_rounds):
            result = page.evaluate(script)
            before = len(seen)
            for message in result.get("messages", []):
                normalized = re.sub(r"\s+", " ", str(message)).strip()
                if len(normalized) >= 2:
                    seen.setdefault(normalized, str(message).strip())
            unchanged = unchanged + 1 if len(seen) == before else 0
            if unchanged >= 4 or result.get("scrollTop") == 0 or len(seen) >= 2500:
                break
            page.wait_for_timeout(250)
        return list(seen.values())

    @staticmethod
    def _save_slack_document(*, project_id: str, title: str, source_ref: str, text: str) -> None:
        source = f"browser_slack:{source_ref}"
        connection = get_connection()
        try:
            rows = connection.execute(
                "SELECT id FROM documents WHERE project_id=? AND source_type=? AND source_ref=?",
                (project_id, "browser_slack", source_ref),
            ).fetchall()
            for row in rows:
                connection.execute("DELETE FROM chunks WHERE document_id=?", (row["id"],))
            connection.execute(
                "DELETE FROM documents WHERE project_id=? AND source_type=? AND source_ref=?",
                (project_id, "browser_slack", source_ref),
            )
            connection.execute(
                "DELETE FROM knowledge WHERE project_id=? AND source=?", (project_id, source)
            )
            connection.execute(
                "DELETE FROM timeline WHERE project_id=? AND source=?", (project_id, source)
            )
            connection.execute(
                "DELETE FROM participants WHERE project_id=? AND source_type=? AND source_ref=?",
                (project_id, "slack", source_ref),
            )
            connection.commit()
        finally:
            connection.close()
        SourceRepository().save_document(
            name=f"Slack: {title}"[:240], source_type="browser_slack",
            source_ref=source_ref, text=text, project_id=project_id,
        )
        MemoryRepository(project_id).save_items([{
            "type": "slack_conversation", "title": title[:240],
            "content": text, "source": source,
        }], default_source="browser_slack")
        extract_participants_from_text(
            text=text, source_type="slack", source_ref=source_ref, project_id=project_id,
        )


local_browser_session_registry = LocalBrowserSessionRegistry()
local_browser_connector_service = LocalBrowserConnectorService(local_browser_session_registry)
