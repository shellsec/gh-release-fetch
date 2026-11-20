"""Build the two assets for the GitHub Releases catalog-data tag."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.catalog_update import ASSET, DIRECTORIES, PLATFORMS, allowed, unpack
from tools import bolesync_catalog, generate_catalog_html


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bolesync-snapshot", type=Path, help="Build with a saved BoleSync feed.")
    options = parser.parse_args()
    feed = (json.loads(options.bolesync_snapshot.read_bytes())
            if options.bolesync_snapshot else bolesync_catalog.fetch())
    switch_dir = ROOT / "apps-switch" / "switch"
    switch_shards = {path.name: json.loads(path.read_bytes()) for path in switch_dir.glob("*.json")}
    count = bolesync_catalog.merge(switch_shards, feed)
    print(f"BoleSync: merged {count} standalone NRO entries")
    generated = {
        f"apps-switch/switch/{name}": json.dumps(rows, ensure_ascii=False, indent=2).encode("utf-8")
        for name, rows in switch_shards.items()
    }
    generated["catalog.html"] = generate_catalog_html.render(
        generate_catalog_html.collect(switch_shards)
    ).encode("utf-8")
    output = ROOT / "dist" / "catalog-data"
    output.mkdir(parents=True, exist_ok=True)
    target = output / ASSET
    members = [ROOT / directory / "root.json" for directory in sorted(DIRECTORIES)]
    for directory, platform in sorted(PLATFORMS):
        if (directory, platform) != ("apps-switch", "switch"):
            members.extend(sorted((ROOT / directory / platform).glob("*.json")))
    temporary = target.with_suffix(".tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in members:
            name = path.relative_to(ROOT).as_posix()
            if allowed(name):
                info = zipfile.ZipInfo(name)
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
        for name, content in sorted(generated.items()):
            archive.writestr(zipfile.ZipInfo(name), content, compress_type=zipfile.ZIP_DEFLATED)
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(dir=output) as validation:
        unpack(temporary, Path(validation))
    temporary.replace(target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(".zip.sha256").write_text(f"{digest}  {target.name}\n", encoding="ascii")
    print(f"{target} ({target.stat().st_size} bytes)\n{digest}")


if __name__ == "__main__":
    main()
