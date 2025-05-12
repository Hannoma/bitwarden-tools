import json
import sys
from pathlib import Path

from data.bitwarden import BitwardenEntry
from utils.logger import logger


class BitwardenWrapper:
    original_data: dict = {} # save other data here (e.g. folders, attachments, etc.)
    other_items: list[dict] = [] # save other items here (e.g. notes, cards, etc.)

    def load(self, path: Path) -> list[BitwardenEntry]:
        password_entries: list[BitwardenEntry] = []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            self.original_data = data

            for item in data.get("items", []):
                if item.get("type") == 1:
                    # Only process login items
                    password_entries.append(BitwardenEntry.from_dict(item))
                else:
                    # Save other items for later processing
                    self.other_items.append(item)

            return password_entries
        except Exception as exc:
            sys.exit(f"[!] Failed to read Bitwarden JSON export: {exc}")


    def save(self, path: Path, entries: list[BitwardenEntry]) -> None:
        entries_dicts = [entry.to_dict() for entry in entries]
        self.original_data["items"] = entries_dicts + self.other_items

        path.write_text(json.dumps(self.original_data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Saved cleaned Bitwarden export to {path}")
