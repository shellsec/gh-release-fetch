"""Verified online search data for software news and games."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
import zipfile

from tools.catalog_update import LIMIT, current_snapshot, update_bundle

ASSET = "gh-release-fetch-page-index.zip"
INDEX = "page-index.json"
CACHE = "page-index-updates"


def unpack(source, destination):
    with zipfile.ZipFile(source) as archive:
        members = archive.infolist()
        if len(members) != 1 or members[0].filename != INDEX or members[0].file_size > LIMIT:
            raise ValueError("Invalid page index archive")
        content = archive.read(members[0])
    indexes = json.loads(content.decode("utf-8"))
    if not isinstance(indexes, dict) or set(indexes) != {"news", "games"}:
        raise ValueError("Invalid page indexes")
    for rows in indexes.values():
        if not isinstance(rows, list) or not rows:
            raise ValueError("Empty page index")
        for row in rows:
            if not isinstance(row, dict) or any(not isinstance(row.get(key), str)
                                               for key in ("url", "title", "scope", "scope_label", "tier", "domain")):
                raise ValueError("Invalid page index entry")
            url = urlsplit(row["url"])
            if url.scheme not in ("http", "https") or not url.hostname or url.username is not None:
                raise ValueError("Invalid page index URL")
            if not isinstance(row.get("software"), list) or not all(isinstance(name, str) for name in row["software"]):
                raise ValueError("Invalid page index keywords")
    (destination / INDEX).write_bytes(content)


def update(root, report, **options):
    return update_bundle(root, report, ASSET, unpack, cache_name=CACHE, marker=INDEX, **options)


def read(root, games):
    path = current_snapshot(Path(root) / CACHE, INDEX) / INDEX
    try:
        return json.loads(path.read_text(encoding="utf-8"))["games" if games else "news"]
    except (OSError, ValueError, KeyError, TypeError):
        return None


def pack(output):
    from tempfile import TemporaryDirectory
    from tools.soft_page_check.search_pages import build_index

    output.mkdir(parents=True, exist_ok=True)
    indexes = {"news": build_index(), "games": build_index(frozenset({"gamer520"}))}
    with TemporaryDirectory(dir=output) as temp:
        staging = Path(temp)
        archive_path = staging / ASSET
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(INDEX, json.dumps(indexes, ensure_ascii=False).encode("utf-8"))
        unpack(archive_path, staging)
        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        archive_path.replace(output / ASSET)
    (output / (ASSET + ".sha256")).write_text(f"{digest}  {ASSET}\n", encoding="ascii")
    print(f"{ASSET}: {len(indexes['news'])} search entries, {len(indexes['games'])} game entries")


if __name__ == "__main__":
    pack(Path("dist/catalog-data"))
