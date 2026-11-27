"""Register GH Release Fetch in an AI client's per-user MCP configuration."""

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import tomlkit

CLIENTS = ("Claude Code", "Codex", "Cursor")
SERVER_ID = "gh_release_fetch"


def configure_client(client, url, token, *, command=None, home=None, env=None):
    home = Path.home() if home is None else Path(home)
    env = os.environ if env is None else env
    if client == "Codex":
        path = Path(env.get("CODEX_HOME") or home / ".codex").expanduser() / "config.toml"
        parse, serialize, key = tomlkit.parse, tomlkit.dumps, "mcp_servers"
        entry = {"url": url, "http_headers": {"Authorization": f"Bearer {token}"}}
    elif client == "Claude Code":
        directory = env.get("CLAUDE_CONFIG_DIR")
        path = (Path(directory).expanduser() if directory else home) / ".claude.json"
        parse, serialize, key = json.loads, format_json, "mcpServers"
        entry = {"type": "http", "url": url, "headers": {"Authorization": f"Bearer {token}"}}
    elif client == "Cursor":
        path = home / ".cursor" / "mcp.json"
        parse, serialize, key = json.loads, format_json, "mcpServers"
        entry = {"url": url, "headers": {"Authorization": f"Bearer {token}"}}
    else:
        raise ValueError("Unknown AI client.")
    if command:
        entry = {"command": command[0], "args": list(command[1:])}
        if client == "Claude Code":
            entry["type"] = "stdio"

    path = path.resolve()
    original = read_config(path)
    text = original.decode("utf-8-sig") if original is not None else "" if client == "Codex" else "{}"
    data = parse(text.replace("\r\n", "\n"))
    if not isinstance(data, dict):
        raise ValueError("The AI client configuration must be a mapping.")
    servers = data.setdefault(key, tomlkit.table() if client == "Codex" else {})
    if not isinstance(servers, dict):
        raise ValueError(f"Unexpected configuration type for {key}.")
    if servers.get(SERVER_ID) == entry:
        return path
    servers[SERVER_ID] = entry
    content = serialize(data)
    if "\r\n" in text:
        content = content.replace("\n", "\r\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(content)
            stream.close()
            if read_config(path) != original:
                raise OSError("The AI client configuration changed while it was being edited. Try again.")
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    return path


def read_config(path):
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def format_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
