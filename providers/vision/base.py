from abc import ABC, abstractmethod
from typing import Callable, List


VisionProgressCallback = Callable[[dict], None]


class VisionProvider(ABC):
    """
    Abstract interface for screen/image analysis providers.

    progress_callback receives events like:
    {
        "event": "frame_started" | "frame_completed" | "frame_failed",
        "current": 1,
        "total": 5,
        "source": "...",
        "items_count": 2,
        "error": "..."
    }
    """

    @abstractmethod
    def analyze_frames(
        self,
        frame_paths: List[str],
        source: str,
        progress_callback: VisionProgressCallback | None = None,
    ) -> list[dict]:
        raise NotImplementedError

