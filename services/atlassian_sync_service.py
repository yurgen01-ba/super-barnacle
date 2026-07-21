from __future__ import annotations

import json
import re
import time
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

from repositories.atlassian_connection_repository import (
    AtlassianConnectionRepository,
    atlassian_connection_repository,
)
from repositories.memory_repository import MemoryRepository
from repositories.source_repository import SourceRepository
from repositories.workspace_repository import workspace_repository
from memory.db import get_connection
from services.atlassian_oauth_service import AtlassianOAuthService, atlassian_oauth_service
from services.participant_extraction_service import extract_participants_from_text


class _HTMLText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def _html_text(value: str | None) -> str:
    parser = _HTMLText()
    parser.feed(str(value or ""))
    return unescape("\n".join(parser.parts))


def _adf_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(_adf_text(item) for item in value)
    if not isinstance(value, dict):
        return str(value)
    node_type = value.get("type")
    text = str(value.get("text", ""))
    children = "".join(_adf_text(item) for item in value.get("content", []))
    if node_type in {"paragraph", "heading", "listItem", "tableRow"}:
        return text + children + "\n"
    if node_type == "hardBreak":
        return "\n"
    return text + children


class AtlassianSyncService:
    def __init__(
        self,
        oauth: AtlassianOAuthService | None = None,
        repository: AtlassianConnectionRepository | None = None,
        client: httpx.Client | None = None,
    ):
        self.oauth = oauth or atlassian_oauth_service
        self.repository = repository or atlassian_connection_repository
        self.client = client or httpx.Client(timeout=90.0, follow_redirects=True)

    def sync(
        self,
        *,
        connection_id: int,
        user_id: str,
        project_id: str,
        sync_jira: bool = True,
        sync_confluence: bool = True,
        progress=None,
    ) -> dict:
        connection, access_token = self.oauth.valid_access_token(connection_id, user_id, project_id)
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        result = {"site": connection["site_name"], "jira": {}, "confluence": {}}
        scopes = set(connection.get("scopes", []))
        try:
            if sync_jira and any("jira" in scope for scope in scopes):
                if progress:
                    progress(0.04, "atlassian:jira", "Reading accessible Jira issues")
                result["jira"] = self._sync_jira(connection, headers, project_id, progress)
            if sync_confluence and any("confluence" in scope for scope in scopes):
                if progress:
                    progress(0.52, "atlassian:confluence", "Reading accessible Confluence content")
                result["confluence"] = self._sync_confluence(connection, headers, project_id, progress)
            self.repository.mark_sync(connection_id, result)
            workspace_repository.log_event(
                project_id, "source", "Atlassian synchronization completed", result
            )
            if progress:
                progress(1.0, "completed", "Atlassian synchronization completed")
            return result
        except Exception as exc:
            self.repository.mark_sync(connection_id, {"error": str(exc)}, status="error")
            raise

    def _request(self, method: str, url: str, headers: dict, **kwargs) -> httpx.Response:
        for attempt in range(4):
            response = self.client.request(method, url, headers=headers, **kwargs)
            if response.status_code != 429:
                response.raise_for_status()
                return response
            wait = min(float(response.headers.get("Retry-After", "1")), 10.0)
            time.sleep(wait * (attempt + 1))
        response.raise_for_status()
        return response

    def _sync_jira(self, connection: dict, headers: dict, project_id: str, progress) -> dict:
        base = f"https://api.atlassian.com/ex/jira/{connection['cloud_id']}"
        last_sync = connection.get("last_sync_at")
        jql = "ORDER BY updated ASC"
        if last_sync:
            moment = datetime.fromisoformat(last_sync).strftime("%Y-%m-%d %H:%M")
            jql = f'updated >= "{moment}" ORDER BY updated ASC'
        next_token = None
        issue_refs: list[dict] = []
        while True:
            params = {"jql": jql, "maxResults": 100, "fields": "key,summary,updated"}
            if next_token:
                params["nextPageToken"] = next_token
            payload = self._request("GET", f"{base}/rest/api/3/search/jql", headers, params=params).json()
            issue_refs.extend(payload.get("issues", []))
            next_token = payload.get("nextPageToken")
            if not next_token or payload.get("isLast") is True:
                break

        saved = 0
        errors: list[str] = []
        for index, ref in enumerate(issue_refs, start=1):
            key = ref.get("key") or ref.get("id")
            try:
                issue = self._request(
                    "GET", f"{base}/rest/api/3/issue/{key}", headers,
                    params={"fields": "*all", "expand": "changelog,names,schema,renderedFields"},
                ).json()
                issue["_all_comments"] = self._jira_paged_values(
                    f"{base}/rest/api/3/issue/{key}/comment", headers, "comments"
                )
                issue["_all_changelog"] = self._jira_paged_values(
                    f"{base}/rest/api/3/issue/{key}/changelog", headers, "values"
                )
                text = self._jira_issue_text(issue)
                self._save_document(
                    project_id=project_id, name=f"{key}: {issue.get('fields', {}).get('summary', '')}",
                    source_type="atlassian_jira", source_ref=str(key), text=text,
                    item_type="jira_issue", item_title=f"{key}: {issue.get('fields', {}).get('summary', '')}",
                )
                saved += 1
            except Exception as exc:
                errors.append(f"{key}: {type(exc).__name__}: {exc}")
            if progress and issue_refs:
                progress(0.05 + 0.43 * index / len(issue_refs), "atlassian:jira", f"Jira {index}/{len(issue_refs)}")
        return {"found": len(issue_refs), "saved": saved, "errors": errors, "incremental": bool(last_sync)}

    def _sync_confluence(self, connection: dict, headers: dict, project_id: str, progress) -> dict:
        base = f"https://api.atlassian.com/ex/confluence/{connection['cloud_id']}"
        content: list[tuple[str, dict]] = []
        for kind, endpoint in (("page", "/wiki/api/v2/pages"), ("blogpost", "/wiki/api/v2/blogposts")):
            url = f"{base}{endpoint}"
            while url:
                response = self._request("GET", url, headers, params={"limit": 100, "body-format": "storage"})
                payload = response.json()
                content.extend((kind, item) for item in payload.get("results", []))
                next_url = payload.get("_links", {}).get("next")
                url = self._confluence_next_url(base, next_url)

        saved = 0
        errors: list[str] = []
        for index, (kind, item) in enumerate(content, start=1):
            content_id = str(item.get("id", ""))
            try:
                details = item
                if not item.get("body"):
                    details = self._request(
                        "GET", f"{base}/wiki/api/v2/{'pages' if kind == 'page' else 'blogposts'}/{content_id}",
                        headers, params={"body-format": "storage"},
                    ).json()
                comments = self._confluence_comments(base, kind, content_id, headers)
                attachments = self._paged_results(
                    f"{base}/wiki/api/v2/{'pages' if kind == 'page' else 'blogposts'}/{content_id}/attachments",
                    base, headers, body_format=False,
                )
                text = self._confluence_content_text(details, comments, attachments)
                self._save_document(
                    project_id=project_id, name=str(details.get("title") or f"Confluence {content_id}"),
                    source_type="atlassian_confluence", source_ref=content_id, text=text,
                    item_type="confluence_page", item_title=str(details.get("title") or f"Confluence {content_id}"),
                )
                saved += 1
            except Exception as exc:
                errors.append(f"{content_id}: {type(exc).__name__}: {exc}")
            if progress and content:
                progress(0.53 + 0.45 * index / len(content), "atlassian:confluence", f"Confluence {index}/{len(content)}")
        return {"found": len(content), "saved": saved, "errors": errors}

    def _jira_paged_values(self, url: str, headers: dict, result_key: str) -> list[dict]:
        items: list[dict] = []
        start_at = 0
        while True:
            try:
                payload = self._request(
                    "GET", url, headers, params={"startAt": start_at, "maxResults": 100}
                ).json()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in {400, 403, 404}:
                    return items
                raise
            page = payload.get(result_key, [])
            items.extend(page)
            start_at += len(page)
            total = int(payload.get("total", len(items)))
            if not page or start_at >= total:
                return items

    def _paged_results(
        self, url: str, base: str, headers: dict, *, body_format: bool = True
    ) -> list[dict]:
        items: list[dict] = []
        while url:
            params = {"limit": 100}
            if body_format:
                params["body-format"] = "storage"
            response = self._request("GET", url, headers, params=params)
            payload = response.json()
            items.extend(payload.get("results", []))
            next_url = payload.get("_links", {}).get("next")
            url = self._confluence_next_url(base, next_url)
        return items

    @staticmethod
    def _confluence_next_url(base: str, next_url: str | None) -> str:
        if not next_url:
            return ""
        if urlparse(next_url).scheme:
            return next_url
        # Atlassian returns paths beginning with /wiki. urljoin() would drop
        # /ex/confluence/{cloudId}, which is required for OAuth 2.0 calls.
        return f"{base.rstrip('/')}/{next_url.lstrip('/')}"

    def _confluence_comments(self, base: str, kind: str, content_id: str, headers: dict) -> list[dict]:
        if kind != "page":
            return []
        comments: list[dict] = []
        for comment_kind in ("footer-comments", "inline-comments"):
            try:
                comments.extend(self._paged_results(
                    f"{base}/wiki/api/v2/pages/{content_id}/{comment_kind}", base, headers
                ))
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in {400, 403, 404}:
                    raise
        return comments

    @staticmethod
    def _jira_issue_text(issue: dict) -> str:
        fields = issue.get("fields", {})
        lines = [
            f"Key: {issue.get('key', '')}", f"Summary: {fields.get('summary', '')}",
            f"Status: {(fields.get('status') or {}).get('name', '')}",
            f"Type: {(fields.get('issuetype') or {}).get('name', '')}",
            f"Project: {(fields.get('project') or {}).get('name', '')}",
            f"Reporter: {(fields.get('reporter') or {}).get('displayName', '')}",
            f"Assignee: {(fields.get('assignee') or {}).get('displayName', '')}",
            f"Created: {fields.get('created', '')}", f"Updated: {fields.get('updated', '')}",
            "", "Description:", _adf_text(fields.get("description")), "", "Comments:",
        ]
        for comment in issue.get("_all_comments") or (fields.get("comment") or {}).get("comments", []):
            lines.append(f"{(comment.get('author') or {}).get('displayName', '')}: {_adf_text(comment.get('body'))}")
        lines.extend(["", "Change history:"])
        for history in issue.get("_all_changelog") or issue.get("changelog", {}).get("histories", []):
            lines.append(f"{history.get('created', '')} — {(history.get('author') or {}).get('displayName', '')}")
            for change in history.get("items", []):
                lines.append(f"  {change.get('field', '')}: {change.get('fromString', '')} -> {change.get('toString', '')}")
        attachments = fields.get("attachment") or []
        if attachments:
            lines.extend(["", "Attachments:"])
            for item in attachments:
                lines.append(f"{item.get('filename', '')} | {item.get('mimeType', '')} | {item.get('content', '')}")
        return "\n".join(str(line) for line in lines).strip()

    @staticmethod
    def _confluence_content_text(details: dict, comments: list[dict], attachments: list[dict]) -> str:
        body = details.get("body", {})
        storage = body.get("storage", body) if isinstance(body, dict) else {}
        value = storage.get("value", "") if isinstance(storage, dict) else str(storage)
        lines = [
            f"Title: {details.get('title', '')}", f"Status: {details.get('status', '')}",
            f"Created: {details.get('createdAt', '')}", "", _html_text(value),
        ]
        if comments:
            lines.extend(["", "Comments:"])
            for comment in comments:
                comment_body = comment.get("body", {})
                storage_body = comment_body.get("storage", comment_body) if isinstance(comment_body, dict) else {}
                lines.append(_html_text(storage_body.get("value", "") if isinstance(storage_body, dict) else str(storage_body)))
        if attachments:
            lines.extend(["", "Attachments:"])
            for item in attachments:
                lines.append(f"{item.get('title', '')} | {item.get('mediaType', '')} | {json.dumps(item.get('_links', {}))}")
        return "\n".join(lines).strip()

    @staticmethod
    def _save_document(
        *, project_id: str, name: str, source_type: str, source_ref: str,
        text: str, item_type: str, item_title: str,
    ) -> None:
        source = f"{source_type}:{source_ref}"
        # Re-sync replaces the previous normalized version of this remote object.
        # This keeps imports idempotent while preserving unrelated project data.
        connection = get_connection()
        try:
            rows = connection.execute(
                "SELECT id FROM documents WHERE project_id=? AND source_type=? AND source_ref=?",
                (project_id, source_type, source_ref),
            ).fetchall()
            for row in rows:
                connection.execute("DELETE FROM chunks WHERE document_id=?", (row["id"],))
            connection.execute(
                "DELETE FROM documents WHERE project_id=? AND source_type=? AND source_ref=?",
                (project_id, source_type, source_ref),
            )
            connection.execute(
                "DELETE FROM knowledge WHERE project_id=? AND source=?", (project_id, source)
            )
            connection.execute(
                "DELETE FROM timeline WHERE project_id=? AND source=?", (project_id, source)
            )
            connection.execute(
                "DELETE FROM participants WHERE project_id=? AND source_type=? AND source_ref=?",
                (
                    project_id,
                    "jira" if "jira" in source_type else "confluence",
                    source_ref,
                ),
            )
            connection.commit()
        finally:
            connection.close()
        SourceRepository().save_document(
            name=name[:240], source_type=source_type, source_ref=source_ref,
            text=text, project_id=project_id,
        )
        MemoryRepository(project_id).save_items([{
            "type": item_type, "title": item_title[:240], "content": text,
            "source": source,
        }], default_source=source_type)
        extract_participants_from_text(
            text=text, source_type="jira" if "jira" in source_type else "confluence",
            source_ref=source_ref, project_id=project_id,
        )


atlassian_sync_service = AtlassianSyncService()
