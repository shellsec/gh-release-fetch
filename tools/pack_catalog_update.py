"""Build the two assets for the GitHub Releases catalog-data tag."""
import hashlib
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.catalog_update import ASSET, DIRECTORIES, PLATFORMS, allowed, unpack


def main():
    output = ROOT / "dist" / "catalog-data"
    output.mkdir(parents=True, exist_ok=True)
    target = output / ASSET
    members = [ROOT / "catalog.html"]
    members.extend(ROOT / directory / "root.json" for directory in sorted(DIRECTORIES))
    for directory, platform in sorted(PLATFORMS):
        members.extend(sorted((ROOT / directory / platform).glob("*.json")))
    temporary = target.with_suffix(".tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in members:
            name = path.relative_to(ROOT).as_posix()
            if allowed(name):
                info = zipfile.ZipInfo(name)
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(dir=output) as validation:
        unpack(temporary, Path(validation))
    temporary.replace(target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(".zip.sha256").write_text(f"{digest}  {target.name}\n", encoding="ascii")
    print(f"{target} ({target.stat().st_size} bytes)\n{digest}")


if __name__ == "__main__":
    main()
