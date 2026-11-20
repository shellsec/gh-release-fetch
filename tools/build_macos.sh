#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != Darwin ]]; then
    echo "Build the macOS app on a Mac." >&2
    exit 1
fi

cd "$(dirname "$0")/.."
python="${PYTHON:-python3}"
arch="$("$python" -c 'import platform; print(platform.machine())')"
case "$arch" in
    arm64|x86_64) ;;
    *) echo "Unsupported macOS Python architecture: $arch" >&2; exit 1 ;;
esac

work="build/macos-$arch"
mkdir -p "$work"
"$python" -m venv "$work/venv"
python="$work/venv/bin/python"
if ! "$python" -c 'import tkinter, _tkinter'; then
    echo "This Python lacks Tk. Use Python from python.org or install the matching python-tk Homebrew formula." >&2
    exit 1
fi
"$python" -m pip install -r requirements.txt 'pyinstaller>=6.11,<7'

printf '%s\n' "0.0" > "$work/ghrf-version.txt"
data=(--add-data "$work/ghrf-version.txt:.")
for directory in apps apps-mobile apps-tv apps-switch apps-ps4 apps-ps5 apps-vita apps-xbox apps-handheld \
    VibeCodingToolsDown/dist/vibecoding tools/soft_page_check/history tools/soft_page_check/list; do
    data+=(--add-data "$directory:$directory")
done
data+=(--add-data "catalog.html:." --add-data "release/windows/gui-icons:gui-icons")
for name in tools/soft_page_check/{soft_pages_urls,watch_tier_a_urls,423down_digest_urls}.txt; do
    if [[ -f "$name" ]]; then
        data+=(--add-data "$name:${name%/*}")
    fi
done

"$python" -m PyInstaller --noconfirm --clean --windowed --onedir \
    --name GHReleaseFetch --osx-bundle-identifier com.shellsec.GHReleaseFetch \
    --target-arch "$arch" --distpath "dist/macos-$arch" --workpath "$work/pyinstaller" --specpath "$work" \
    --hidden-import tools.app_list --hidden-import tools.ghrf_runtime --hidden-import tools.apply_enabled_snapshot \
    "${data[@]}" windows_gui.py

echo "Built dist/macos-$arch/GHReleaseFetch.app"
