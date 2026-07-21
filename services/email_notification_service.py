from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class EmailNotificationService:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "").strip()
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME", "").strip()
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.sender = os.getenv("SMTP_FROM", self.username).strip()
        self.use_tls = _as_bool(os.getenv("SMTP_USE_TLS"), default=True)
        self.use_ssl = _as_bool(os.getenv("SMTP_USE_SSL"), default=False)

    @property
    def is_configured(self) -> bool:
        return bool(self.host and self.sender)

    def send(self, *, recipient: str, subject: str, body: str) -> bool:
        if not self.is_configured or not recipient:
            return False
        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(str(body), subtype="plain", charset="utf-8")

        smtp_class = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        with smtp_class(self.host, self.port, timeout=30) as smtp:
            if self.use_tls and not self.use_ssl:
                smtp.starttls()
            if self.username:
                smtp.login(self.username, self.password)
            smtp.send_message(message)
        return True

    def send_verification_email(self, *, recipient: str, name: str, verification_url: str) -> bool:
        subject = "Project Brain: подтвердите адрес электронной почты"
        body = (
            f"Здравствуйте, {name or 'пользователь'}!\n\n"
            "Чтобы завершить регистрацию в Project Brain, подтвердите адрес электронной почты:\n"
            f"{verification_url}\n\n"
            "Ссылка действует 24 часа. Если вы не создавали аккаунт, просто проигнорируйте письмо."
        )
        return self.send(recipient=recipient, subject=subject, body=body)

    def notify_job_finished(self, job) -> bool:
        recipient = str((job.metadata or {}).get("notification_email") or "").strip()
        if not recipient:
            return False
        source = (job.metadata or {}).get("source", "источник данных")
        if job.status == "completed":
            subject = "Project Brain: обработка данных завершена"
            body = (
                f"Обработка источника «{source}» завершена.\n\n"
                "Откройте Project Brain, чтобы посмотреть результат.\n"
                f"Job ID: {job.id}"
            )
        else:
            subject = "Project Brain: обработка данных завершилась с ошибкой"
            body = (
                f"При обработке источника «{source}» произошла ошибка.\n\n"
                f"{job.error or 'Подробности доступны в журнале задачи.'}\n"
                f"Job ID: {job.id}"
            )
        return self.send(recipient=recipient, subject=subject, body=body)


email_notification_service = EmailNotificationService()
