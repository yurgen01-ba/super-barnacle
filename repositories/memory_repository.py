from memory.deduplicator import DecisionDeduplicator
from memory.project_memory import ProjectMemory
from memory.schema import KnowledgeItem
from memory.timeline import Timeline


class MemoryRepository:
    def __init__(self):
        self.memory = ProjectMemory()
        self.timeline = Timeline()
        self.dedup = DecisionDeduplicator(existing_items=self.memory.get_all())

    def save_items(self, items, default_source: str = "unknown"):
        saved = 0
        skipped = 0
        errors = []

        if not items:
            return saved, skipped, ["No items returned by extractor"]

        for item in items:
            try:
                if not isinstance(item, dict):
                    errors.append(f"Invalid item type: {type(item)}; value={item}")
                    continue

                item_type = item.get("type") or "unknown"
                title = item.get("title") or item.get("name") or "Untitled"
                content = item.get("content") or item.get("description") or str(item)
                source = item.get("source") or default_source

                normalized_item = {
                    "type": str(item_type),
                    "title": str(title),
                    "content": str(content),
                    "source": str(source),
                }

                if normalized_item["type"] == "decision" and self.dedup.is_duplicate(normalized_item["title"]):
                    skipped += 1
                    continue

                self.memory.add(KnowledgeItem(**normalized_item))
                self.timeline.add_event(
                    event_type=normalized_item["type"],
                    title=normalized_item["title"],
                    source=normalized_item["source"],
                )
                saved += 1

            except Exception as exc:
                errors.append(f"Failed to save item {item}: {repr(exc)}")

        return saved, skipped, errors

    def get_memory_items(self):
        return self.memory.get_all()

    def get_timeline_items(self):
        return self.timeline.get_all()

    def clear(self):
        self.memory.clear()
        self.timeline.clear()

