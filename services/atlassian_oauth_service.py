from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx

from repositories.atlassian_connection_repository import (
    AtlassianConnectionRepository,
    atlassian_connection_repository,
)


ATLASSIAN_BASE_SCOPES = "offline_access read:me"
ATLASSIAN_JIRA_SCOPES = "read:jira-work read:jira-user"
ATLASSIAN_CONFLUENCE_SCOPES = (
    "read:confluence-content.all read:confluence-space.summary "
    "search:confluence read:attachment:confluence"
)
ATLASSIAN_SCOPES = " ".join(
    (ATLASSIAN_BASE_SCOPES, ATLASSIAN_JIRA_SCOPES, ATLASSIAN_CONFLUENCE_SCOPES)
)


class AtlassianOAuthError(RuntimeError):
    pass


class AtlassianOAuthService:
    def __init__(
        self,
        repository: AtlassianConnectionRepository | None = None,
        client: httpx.Client | None = None,
    ):
        self.repository = repository or atlassian_connection_repository
        self.client_id = os.getenv("ATLASSIAN_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("ATLASSIAN_CLIENT_SECRET", "").strip()
        self.redirect_uri = os.getenv(
            "ATLASSIAN_REDIRECT_URI",
            os.getenv("APP_BASE_URL", "http://localhost:8501").rstrip("/") + "/?atlassian_callback=1",
        ).strip()
        self.client = client or httpx.Client(timeout=60.0, follow_redirects=True)

    @property
    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.redirect_uri)

    def authorization_url(
        self, user_id: str, project_id: str, *, product: str | None = None
    ) -> str:
        if not self.configured:
            raise AtlassianOAuthError("Atlassian OAuth is not configured")
        product = str(product or "").strip().lower()
        if product == "jira":
            scopes = " ".join((ATLASSIAN_BASE_SCOPES, ATLASSIAN_JIRA_SCOPES))
        elif product == "confluence":
            scopes = " ".join((ATLASSIAN_BASE_SCOPES, ATLASSIAN_CONFLUENCE_SCOPES))
        elif not product:
            scopes = ATLASSIAN_SCOPES
        else:
            raise AtlassianOAuthError(f"Unsupported Atlassian product: {product}")
        state = self.repository.create_state(user_id, project_id)
        return "https://auth.atlassian.com/authorize?" + urlencode({
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "scope": scopes,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "response_type": "code",
            "prompt": "consent",
        })

    def complete_authorization(self, code: str, state: str) -> dict:
        if not self.configured:
            raise AtlassianOAuthError("Atlassian OAuth is not configured")
        if not code or not state:
            raise AtlassianOAuthError("Atlassian callback is missing code or state")
        state_data = self.repository.consume_state(state)
        if not state_data:
            raise AtlassianOAuthError("OAuth state is invalid or expired")
        response = self.client.post(
            "https://auth.atlassian.com/oauth/token",
            json={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": self.redirect_uri,
            },
        )
        self._raise(response, "Atlassian did not issue an access token")
        token = response.json()
        access_token = token.get("access_token", "")
        resources = self.client.get(
            "https://api.atlassian.com/oauth/token/accessible-resources",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        self._raise(resources, "Unable to read accessible Atlassian sites")
        sites = resources.json()
        if not sites:
            raise AtlassianOAuthError("No accessible Jira or Confluence sites were returned")
        connections = self.repository.save_sites(
            user_id=state_data["user_id"], project_id=state_data["project_id"],
            sites=sites, access_token=access_token,
            refresh_token=token.get("refresh_token"), expires_in=token.get("expires_in"),
        )
        return {"sites": sites, "connections": connections, **state_data}

    def valid_access_token(self, connection_id: int, user_id: str, project_id: str) -> tuple[dict, str]:
        connection = self.repository.get_with_tokens(connection_id, user_id, project_id)
        if not connection:
            raise AtlassianOAuthError("Atlassian connection was not found")
        expires_at = connection.get("expires_at")
        if expires_at and datetime.fromisoformat(expires_at) > datetime.now(timezone.utc) + timedelta(seconds=60):
            return connection, connection["access_token"]
        refresh_token = connection.get("refresh_token")
        if not refresh_token:
            raise AtlassianOAuthError("Atlassian authorization expired; reconnect the account")
        response = self.client.post(
            "https://auth.atlassian.com/oauth/token",
            json={
                "grant_type": "refresh_token", "client_id": self.client_id,
                "client_secret": self.client_secret, "refresh_token": refresh_token,
            },
        )
        self._raise(response, "Unable to refresh Atlassian authorization")
        token = response.json()
        self.repository.update_tokens(
            connection_id,
            user_id,
            project_id,
            token["access_token"],
            token.get("refresh_token"),
            token.get("expires_in", 3600),
        )
        return connection, token["access_token"]

    @staticmethod
    def _raise(response: httpx.Response, message: str) -> None:
        if response.is_success:
            return
        detail = response.text[:500]
        raise AtlassianOAuthError(f"{message} ({response.status_code}): {detail}")


atlassian_oauth_service = AtlassianOAuthService()
