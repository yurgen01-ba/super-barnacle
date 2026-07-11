from __future__ import annotations

from models.transcript_segment import TranscriptSegment


class TranscriptSegmentRepository:
    """
    Stores transcript segments immediately after each segment is transcribed.

    Runtime repository for now. It can later be moved to SQLite.
    """

    def __init__(self):
        self._segments: dict[str, TranscriptSegment] = {}
        self._hash_index: set[str] = set()

    def save_segment(
        self,
        source: str,
        file_name: str,
        segment_no: int,
        total_segments: int,
        text: str,
        project_id: str = "default",
        metadata: dict | None = None,
    ) -> TranscriptSegment:
        segment = TranscriptSegment.create(
            source=source,
            file_name=file_name,
            segment_no=segment_no,
            total_segments=total_segments,
            text=text,
            project_id=project_id,
            metadata=metadata,
        )

        if segment.text_hash in self._hash_index:
            return segment

        self._segments[segment.id] = segment
        self._hash_index.add(segment.text_hash)
        return segment

    def list_segments(
        self,
        source: str | None = None,
        file_name: str | None = None,
        project_id: str = "default",
    ) -> list[TranscriptSegment]:
        segments = [
            segment
            for segment in self._segments.values()
            if segment.project_id == project_id
        ]

        if source:
            segments = [segment for segment in segments if segment.source == source]

        if file_name:
            segments = [segment for segment in segments if segment.file_name == file_name]

        return sorted(segments, key=lambda segment: (segment.file_name, segment.segment_no))


transcript_segment_repository = TranscriptSegmentRepository()
