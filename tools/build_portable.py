#!/usr/bin/env python3
"""Build relocatable Unix distributions using uv's standalone CPython runtimes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = {
    'gh-release-fetch-gui': 'windows_gui.py',
    'auto_update': 'auto_update.py',
    'lookup_app': 'lookup_app.py',
    'run_saved_apps': 'tools/run_saved_apps.py',
    'search_soft_pages': 'tools/soft_page_check/search_pages.py',
    'search_games': 'tools/soft_page_check/search_games.py',
}
TARGETS = {
    'macos-arm64': ('macos-aarch64-none', 'aarch64-apple-darwin'),
    'linux-x86_64': ('linux-x86_64-gnu', 'x86_64-unknown-linux-gnu'),
    'linux-arm64': ('linux-aarch64-gnu', 'aarch64-unknown-linux-gnu'),
}

def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--compiler', required=True, help='Host CPython 3.12 executable')
    args = ap.parse_args()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    out = ROOT / 'dist/release'
    out.mkdir(parents=True, exist_ok=True)
    checksums = []
    for label, (runtime_key, platform) in TARGETS.items():
        name = f'gh-release-fetch-{commit[:7]}-{label}'
        stage = ROOT / 'build/portable' / name
        if stage.exists():
            shutil.rmtree(stage)
        stage.mkdir(parents=True)
        for rel in files:
            if not rel or rel.endswith(('.exe', '.bat', '.ps1', '.pyc')) or '__pycache__' in rel or rel == 'update_log.txt':
                continue
            dest = stage / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        runtime = next((ROOT / 'build/portable-runtimes').glob(f'cpython-3.12.*-{runtime_key}'))
        shutil.copytree(runtime, stage / 'runtime', symlinks=True)
        run('uv', 'pip', 'install', '--python', args.compiler, '--python-version', '3.12', '--python-platform', platform,
            '--only-binary', ':all:', '--target', str(stage / 'vendor'), '--cache-dir', str(ROOT / 'build/uv-cache'),
            '-r', str(ROOT / 'requirements.txt'))
        for command, entry in ENTRIES.items():
            launcher = stage / command
            launcher.write_text('#!/bin/sh\nset -eu\nROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\n'
                'export PYTHONNOUSERSITE=1\nexport PYTHONPATH="$ROOT/vendor:$ROOT"\n'
                'cd "$ROOT"\nexec "$ROOT/runtime/bin/python3.12" "$ROOT/' + entry + '" "$@"\n')
            launcher.chmod(0o755)
        run(args.compiler, '-m', 'compileall', '-q', '-s', str(stage), '-p', '.', str(stage))
        metadata = {'source_commit': commit, 'target': label, 'format': 'Standalone CPython + compiled Python bytecode',
                    'python': runtime.name, 'linux_requirement': 'glibc Linux (not Alpine/musl)',
                    'runtime_tested': label == 'macos-arm64'}
        (stage / 'BUILD-INFO.json').write_text(json.dumps(metadata, indent=2) + '\n')
        (stage / 'PORTABLE-README.txt').write_text(
            'GH Release Fetch portable distribution\nSource: ' + commit + '\nTarget: ' + label + '\n\n'
            'Extract the archive, then run ./lookup_app --help or ./auto_update --help.\n'
            'Python and dependencies are bundled. Keep the entire folder together.\n'
            'This is a Python bytecode distribution, not a single native executable.\n'
            'macOS arm64 was smoke-tested; Linux packages require validation on Linux.\n'
            'Linux requires glibc; macOS binaries are not signed or notarized.\n')
        archive = out / (name + '.tar.gz')
        with tarfile.open(archive, 'w:gz') as tar:
            tar.add(stage, arcname=name)
        checksums.append(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name)
        print(archive, flush=True)
    (out / 'SHA256SUMS').write_text('\n'.join(checksums) + '\n')

if __name__ == '__main__':
    main()
