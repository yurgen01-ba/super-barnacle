from __future__ import annotations

import os
from urllib.parse import urlencode

import httpx

from repositories.slack_connection_repository import (
    SlackConnectionRepository,
    slack_connection_repository,
)


SLACK_USER_SCOPES = (
    "channels:history,channels:read,groups:history,groups:read,"
    "im:history,im:read,mpim:history,mpim:read,users:read"
)


class SlackOAuthError(RuntimeError):
    pass


class SlackOAuthService:
    def __init__(
        self,
        repository: SlackConnectionRepository | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.repository = repository or slack_connection_repository
        self.client_id = os.getenv("SLACK_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("SLACK_CLIENT_SECRET", "").strip()
        self.redirect_uri = os.getenv(
            "SLACK_REDIRECT_URI",
            os.getenv("APP_BASE_URL", "http://localhost:8501").rstrip("/")
            + "/?slack_callback=1",
        ).strip()
        self.client = client or httpx.Client(timeout=60.0, follow_redirects=True)

    @property
    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.redirect_uri)

    def authorization_url(self, user_id: str, project_id: str) -> str:
        if not self.configured:
            raise SlackOAuthError("Slack OAuth is not configured")
        state = self.repository.create_state(user_id, project_id)
        return "https://slack.com/oauth/v2/authorize?" + urlencode({
            "client_id": self.client_id,
            "user_scope": SLACK_USER_SCOPES,
            "redirect_uri": self.redirect_uri,
            "state": state,
        })

    def complete_authorization(self, code: str, state: str) -> dict:
        if not self.configured:
            raise SlackOAuthError("Slack OAuth is not configured")
        if not code or not state:
            raise SlackOAuthError("Slack callback is missing code or state")
        state_data = self.repository.consume_state(state)
        if not state_data:
            raise SlackOAuthError("Slack OAuth state is invalid or expired")
        response = self.client.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": self.redirect_uri,
            },
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            raise SlackOAuthError(str(payload.get("error") or "Slack authorization failed"))
        authed_user = payload.get("authed_user") or {}
        enterprise = payload.get("enterprise") or {}
        access_token = str(authed_user.get("access_token") or "")
        if not access_token:
            raise SlackOAuthError("Slack did not issue a user access token")
        team = payload.get("team") or {}
        scopes = [item for item in str(authed_user.get("scope") or "").split(",") if item]
        connection = self.repository.save(
            user_id=state_data["user_id"], project_id=state_data["project_id"],
            team_id=str(team.get("id") or enterprise.get("id") or "unknown"),
            team_name=str(team.get("name") or enterprise.get("name") or "Slack"),
            authed_user_id=str(authed_user.get("id") or ""), scopes=scopes,
            access_token=access_token, refresh_token=authed_user.get("refresh_token"),
            expires_in=authed_user.get("expires_in"),
        )
        return {"connection": connection, **state_data}

    def disconnect(self, connection_id: int, user_id: str, project_id: str) -> bool:
        connection = self.repository.get_with_token(connection_id, user_id, project_id)
        if not connection:
            return False
        try:
            try:
                self.client.post(
                    "https://slack.com/api/auth.revoke",
                    headers={"Authorization": f"Bearer {connection['access_token']}"},
                )
            except httpx.HTTPError:
                # Local disconnect must still work if Slack is temporarily unavailable.
                pass
        finally:
            self.repository.delete(connection_id, user_id, project_id)
        return True


slack_oauth_service = SlackOAuthService()
