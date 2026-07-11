class DecisionDeduplicator:
    def __init__(self, existing_items=None):
        self.seen = set()
        if existing_items:
            for item in existing_items:
                if item.get("type") == "decision":
                    self.seen.add(self._key(item.get("title", "")))

    def _key(self, title: str):
        return " ".join((title or "").lower().strip().split())

    def is_duplicate(self, title: str):
        key = self._key(title)
        if key in self.seen:
            return True
        self.seen.add(key)
        return False

