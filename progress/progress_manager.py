import time
from dataclasses import dataclass
from typing import Optional

import streamlit as st


@dataclass
class ProgressState:
    title: str
    current_step: int
    total_steps: int
    message: str
    details: Optional[str] = None


class ProgressManager:
    def __init__(self, title: str, total_steps: int = 1):
        self.title = title
        self.total_steps = max(total_steps, 1)
        self.current_step = 0
        self.started_at = time.time()

        self.container = st.container()
        with self.container:
            st.markdown(f"### {title}")
            self.status_slot = st.empty()
            self.progress_slot = st.progress(0)
            self.details_slot = st.empty()
            self.time_slot = st.empty()

        self.update("Starting...")

    def elapsed_text(self) -> str:
        elapsed = int(time.time() - self.started_at)
        minutes = elapsed // 60
        seconds = elapsed % 60
        if minutes:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def update(self, message: str, value: float | None = None, details: str | None = None):
        if value is None:
            value = self.current_step / self.total_steps

        value = max(0.0, min(1.0, float(value)))

        self.status_slot.info(message)
        self.progress_slot.progress(value)
        self.time_slot.caption(f"Elapsed: {self.elapsed_text()}")

        if details:
            self.details_slot.caption(details)

    def step(self, message: str, details: str | None = None):
        self.current_step += 1
        self.update(message, details=details)

    def substep(self, message: str, index: int, total: int, details: str | None = None):
        total = max(total, 1)
        base = self.current_step / self.total_steps
        step_size = 1 / self.total_steps
        value = base + step_size * (index / total)
        self.update(message, value=value, details=details)

    def done(self, message: str = "Completed"):
        self.current_step = self.total_steps
        self.update(message, value=1.0)
        self.status_slot.success(message)

    def error(self, message: str):
        self.status_slot.error(message)

