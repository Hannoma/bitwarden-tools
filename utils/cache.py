import json

from data.bitwarden import BitwardenEntry
from data.internal import MergeOperation
from utils.logger import logger

CACHE_FILE = "cache.json"

class Cache:
    # (source_id, source_fingerprint) -> (target_id, target_fingerprint)
    merge_operations: dict[tuple[str, str], tuple[str, str]] = {}

    def __init__(self):
        """Initialize the cache and load existing merge operations."""
        self.load()

    def load(self):
        """Load merge operations from the cache file."""
        try:
            with open(CACHE_FILE, "r") as f:
                merge_operations = [MergeOperation.from_dict(item) for item in json.load(f)]
                self.merge_operations = {
                    (op.source_id, op.source_fingerprint): (op.target_id, op.target_fingerprint)
                    for op in merge_operations
                }
        except FileNotFoundError:
            self.merge_operations = {}
        except json.JSONDecodeError:
            logger.warning("Cache file is corrupted. Starting with an empty cache.")
            self.merge_operations = {}

    def save(self):
        """Save merge operations to the cache file."""
        with open(CACHE_FILE, "w") as f:
            merge_operations = [
                MergeOperation(source_id=source_id, target_id=target_id, source_fingerprint=source_fingerprint, target_fingerprint=target_fingerprint)
                for (source_id, source_fingerprint), (target_id, target_fingerprint) in self.merge_operations.items()
            ]
            json.dump([item.to_dict() for item in merge_operations], f, indent=2)

    def exists(self, source: BitwardenEntry) -> bool:
        """Check if a merge operation exists in the cache."""
        return (source.id, source.get_fingerprint()) in self.merge_operations

    def add(self, source: BitwardenEntry, target: BitwardenEntry):
        """Add a merge operation to the cache."""
        self.merge_operations[(source.id, source.get_fingerprint())] = (target.id, target.get_fingerprint())
        logger.debug(f"Added merge operation to cache: {source.id} -> {target.id}")
        self.save()

    def replay(self, source: BitwardenEntry, items: list[BitwardenEntry]) -> BitwardenEntry | None:
        """Replay a merge operation from the cache."""
        if not self.exists(source):
            return None

        merged = None
        target_id, target_fingerprint = self.merge_operations[(source.id, source.get_fingerprint())]
        for item in items:
            if item.id == target_id and item.get_fingerprint() == target_fingerprint:
                logger.info(f"Replaying merge operation: {source.id} -> {item.id}")
                merged = item.merge(source)
                break

        if merged:
            items.remove(source)

        return merged


cache = Cache()