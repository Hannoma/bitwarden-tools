from dataclasses import dataclass

from data.bitwarden import BitwardenEntry


@dataclass
class MergeOperation:
    """Represents a merge operation for a Bitwarden entry."""

    target_id: str
    target_fingerprint: str
    source_id: str
    source_fingerprint: str

    @classmethod
    def create(cls, source: BitwardenEntry, target: BitwardenEntry) -> "MergeOperation":
        """Create a merge operation from source and target entries."""
        return cls(
            target_id=target.id,
            target_fingerprint=target.get_fingerprint(),
            source_id=source.id,
            source_fingerprint=source.get_fingerprint(),
        )

    @classmethod
    def from_dict(cls, data: dict) -> "MergeOperation":
        return cls(
            target_id=data["target_id"],
            target_fingerprint=data["target_fingerprint"],
            source_id=data["source_id"],
            source_fingerprint=data["source_fingerprint"],
        )

    def to_dict(self) -> dict:
        return {
            "target_id": self.target_id,
            "target_fingerprint": self.target_fingerprint,
            "source_id": self.source_id,
            "source_fingerprint": self.source_fingerprint,
        }


