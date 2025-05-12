import hashlib
import json
import uuid
from datetime import datetime
from typing import Optional

from dataclasses import dataclass, field

from utils.logger import logger
from utils.url import shorten_uri, normalise_domain


@dataclass
class UriEntry:
    """Represents an entry inside `login.uris`."""

    uri: str
    match: Optional[int] = None  # 0‑exact, 1‑host, 2‑starts‑with, … (Bitwarden def)

    def to_dict(self) -> dict:  # helper for JSON serialisation
        return {"match": self.match, "uri": self.uri}

    @staticmethod
    def from_dict(data: dict) -> "UriEntry":
        return UriEntry(uri=data.get("uri", ""), match=data.get("match"))


@dataclass
class LoginData:
    """Represents the `login` section of a Bitwarden entry."""

    username: str = ""
    password: str = ""
    uris: list[UriEntry] = field(default_factory=list)
    fido2Credentials: list[dict] = field(default_factory=list)
    totp: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "fido2Credentials": self.fido2Credentials or [],
            "uris": [u.to_dict() for u in self.uris] or None,
            "username": self.username or None,
            "password": self.password or None,
            "totp": self.totp,
        }

    @staticmethod
    def from_dict(data: dict) -> "LoginData":
        return LoginData(
            username=data.get("username", ""),
            password=data.get("password", ""),
            uris=[UriEntry.from_dict(u) for u in data.get("uris", [])],
            fido2Credentials=data.get("fido2Credentials", []),
            totp=data.get("totp"),
        )


@dataclass
class BitwardenEntry:
    """Top‑level Bitwarden item (only *login* type relevant for this tool)."""

    id: str
    type: int  # 1 = login, 2 = secure note, …
    name: str
    favorite: bool = False
    login: LoginData = field(default_factory=LoginData)
    passwordHistory: Optional[list] = None
    revisionDate: Optional[datetime] = None
    creationDate: Optional[datetime] = None
    deletedDate: Optional[datetime] = None
    organizationId: Optional[str] = None
    folderId: Optional[str] = None
    reprompt: int = 0
    notes: Optional[str] = None
    collectionIds: Optional[list] = None


    def merge(self, other: "BitwardenEntry") -> "BitwardenEntry":
        """Merge another BitwardenEntry into this one

        This function merges the `login` data of the source entry into the target
        entry, ensuring that duplicate URIs are not added.
        """
        # Merge URIs, avoiding duplicates
        existing_uris = {u.uri for u in self.login.uris}
        for uri_entry in other.login.uris:
            shortened_uri = shorten_uri(uri_entry.uri)
            if shortened_uri and shortened_uri not in existing_uris:
                self.login.uris.append(UriEntry(
                    match=uri_entry.match,
                    uri=shortened_uri,
                ))
                existing_uris.add(shortened_uri)
                logger.debug(f"Added uri {shortened_uri} to {self.name} ({self.id}) from {other.name} ({other.id})")

        logger.debug(f"Merged {other.name} ({other.id}) into {self.name} ({self.id})")

        return self


    def get_fingerprint(self) -> str:
        """Get a fingerprint for this entry.

        The fingerprint is a hash of the entry's login data, including the username and password.
        """
        data = {
            "username": self.login.username,
            "password": self.login.password,
            # "uris": [normalise_domain(u.uri) for u in self.login.uris],
        }
        # Sort the URIs to ensure consistent hashing
        # data["uris"].sort()
        # Hash the data to create a fingerprint
        fingerprint = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        return str(fingerprint)


    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------
    @staticmethod
    def from_dict(data: dict) -> "BitwardenEntry":
        """Create a `BitwardenEntry` from raw JSON dict."""
        parse_dt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None
        return BitwardenEntry(
            id=data.get("id", str(uuid.uuid4())),
            type=data.get("type", 1),
            name=data.get("name", ""),
            favorite=bool(data.get("favorite")),
            login=LoginData.from_dict(data.get("login", {})),
            passwordHistory=data.get("passwordHistory"),
            revisionDate=parse_dt(data.get("revisionDate")),
            creationDate=parse_dt(data.get("creationDate")),
            deletedDate=parse_dt(data.get("deletedDate")),
            organizationId=data.get("organizationId"),
            folderId=data.get("folderId"),
            reprompt=data.get("reprompt", 0),
            notes=data.get("notes"),
            collectionIds=data.get("collectionIds"),
        )

    def to_dict(self) -> dict:
        """Serialise back into Bitwarden's JSON shape."""
        fmt_dt = lambda dt: dt.isoformat().replace("000+00:00", "Z") if dt else None
        return {
            "passwordHistory": self.passwordHistory,
            "revisionDate": fmt_dt(self.revisionDate),
            "creationDate": fmt_dt(self.creationDate),
            "deletedDate": fmt_dt(self.deletedDate),
            "id": self.id,
            "organizationId": self.organizationId,
            "folderId": self.folderId,
            "type": self.type,
            "reprompt": self.reprompt,
            "name": self.name or None,
            "notes": self.notes,
            "favorite": self.favorite,
            "login": self.login.to_dict(),
            "collectionIds": self.collectionIds,
        }
