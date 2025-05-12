import csv
import uuid
from pathlib import Path

from data.bitwarden import BitwardenEntry, LoginData, UriEntry
from utils.logger import logger
from utils.url import shorten_uri


def chrome_csv_to_items(csv_path: Path) -> list[BitwardenEntry]:
    """Convert Chrome passwords CSV → Bitwarden‑style items list."""
    items: list[BitwardenEntry] = []
    with (csv_path.open(newline="", encoding="utf-8") as fh):
        reader = csv.DictReader(fh)
        for row in reader:
            url = row.get("url") or row.get("origin") or row.get("URL") or ""
            username = row.get("username") or row.get("accountName") or row.get("Username") or ""
            password = row.get("password") or row.get("Password") or ""
            if not (url or username or password):
                continue  # Skip empty rows
            # create id based on the username and password and name of the entry
            # this is to ensure that the same entry is not created multiple times
            # if the same entry is already present in the vault
            new_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"{username}{password}{row.get('name')}"))
            item = BitwardenEntry(
                id=new_id,
                type=1,
                name=row.get("name"),
                favorite=False,
                login=LoginData(
                    username=username,
                    password=password,
                    uris=[UriEntry(
                        uri=shorten_uri(url),
                    )],
                ),
            )
            items.append(item)

    logger.info(f"Imported {len(items)} from Google Chrome passwords file")
    return items