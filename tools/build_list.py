#!/usr/bin/env python3
"""Builds addons.json from addons/<id>/addon.json and the icon beside it, and checks every
entry against the rules the openOMSI launcher holds it to before it shows one.

    python3 tools/build_list.py           write addons.json
    python3 tools/build_list.py --check   fail when an entry breaks a rule or addons.json is
                                          not what this script writes (CI)

The launcher reads addons.json from this repository's main branch every time the Add-ons page
opens, and shows an icon only when its size and SHA-256 are the list's, so addons.json must be
rebuilt with every change of an entry. Needs nothing but Python 3.8+.
"""
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ADDONS = ROOT / "addons"
LIST = ROOT / "addons.json"
VERSION = 1

PLAIN = re.compile(r"^[a-z0-9-]+$")
ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,39}$")
FIELDS = {"id", "name", "author", "description", "translations", "homepage", "icon", "tags"}
ICONS = {"icon.svg", "icon.png"}
MAX_ICON = 10_000
# (what an SVG may not hold: the launcher shows it as a picture, but nothing in it should run
# or reach the web)
SVG_BANNED = re.compile(r"<script|<foreignobject|\son[a-z]+\s*=|javascript:|(?:href|src)\s*=\s*[\"']?\s*(?:https?:|//|data:)|@import|url\(\s*[\"']?\s*(?:https?:|//)", re.I)
HOMEPAGE_ODD = set("\\\"'<>^`{}|")


def homepage_ok(text):
    """A plain https address of a named website (the launcher checks it again, as the browser
    reads it): no user name or password, no port, no IP address or localhost."""
    if not isinstance(text, str) or not text.startswith("https://") or len(text) > 200:
        return False
    if any(c.isspace() or ord(c) < 32 or c in HOMEPAGE_ODD for c in text):
        return False
    u = urlsplit(text)
    host = (u.hostname or "").lower()
    return (u.username is None and u.password is None and u.port is None
            and "@" not in u.netloc and ":" not in u.netloc
            and "." in host and not host.endswith(".") and not re.match(r"^[\d.]+$", host)
            and host != "localhost" and not host.endswith(".localhost")
            and re.match(r"^[a-z0-9.-]+$", host) is not None)


def problems_of(folder: Path):
    """(entry for the list or None, list of problems)"""
    name, out = folder.name, []
    try:
        meta = json.loads((folder / "addon.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, [f"{name}/addon.json: {e}"]
    if not isinstance(meta, dict):
        return None, [f"{name}/addon.json: an object is needed"]
    for k in sorted(set(meta) - FIELDS):
        out.append(f"{name}: unknown field {k!r}")
    short = lambda v, n: isinstance(v, str) and 0 < len(v.strip()) and len(v) <= n and "\n" not in v
    if meta.get("id") != name or not ID.match(name):
        out.append(f"{name}: id must be the folder's name, 2-40 of a-z 0-9 -")
    for k, n in (("name", 40), ("author", 40), ("description", 200)):
        if not short(meta.get(k), n):
            out.append(f"{name}: {k} is needed, one line of at most {n} characters")
    tr = meta.get("translations", {})
    if not isinstance(tr, dict) or not all(isinstance(l, str) and PLAIN.match(l) and len(l) <= 8 and short(d, 200) for l, d in tr.items()):
        out.append(f"{name}: translations are {{language code: description of at most 200 characters}}")
    if not homepage_ok(meta.get("homepage")):
        out.append(f"{name}: homepage must be a plain https address of a named website (no port, IP, localhost, user name)")
    tags = meta.get("tags", [])
    if not isinstance(tags, list) or len(tags) > 5 or not all(isinstance(t, str) and PLAIN.match(t) and len(t) <= 20 for t in tags):
        out.append(f"{name}: tags must be at most 5 of a-z 0-9 -, each at most 20 characters")

    icon = None
    if "icon" in meta:
        file = meta["icon"]
        path = folder / file if isinstance(file, str) else None
        if file not in ICONS:
            out.append(f"{name}: icon must be icon.svg or icon.png beside addon.json")
        elif path.is_symlink() or not path.is_file():
            out.append(f"{name}: {file} is missing")
        else:
            data = path.read_bytes()
            if len(data) > MAX_ICON:
                out.append(f"{name}/{file}: {len(data)} bytes, at most {MAX_ICON}")
            if file.endswith(".png") and not data.startswith(b"\x89PNG\r\n\x1a\n"):
                out.append(f"{name}/{file}: not a PNG")
            if file.endswith(".svg"):
                text = data.decode("utf-8", "replace")
                if "<svg" not in text:
                    out.append(f"{name}/{file}: not an SVG")
                if SVG_BANNED.search(text):
                    out.append(f"{name}/{file}: no scripts, event handlers or links to other files")
            icon = {"file": file, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    for p in sorted(folder.rglob("*")):
        rel = p.relative_to(folder).as_posix()
        if rel != "addon.json" and rel != meta.get("icon"):
            out.append(f"{name}/{rel}: only addon.json and the icon go into the folder")

    entry = {k: meta[k] for k in ("id", "name", "author", "description", "translations", "homepage") if k in meta}
    if icon:
        entry["icon"] = icon
    entry["tags"] = tags if isinstance(tags, list) else []
    return entry, out


def build():
    entries, problems = [], []
    for folder in sorted(p for p in ADDONS.iterdir() if p.is_dir()) if ADDONS.is_dir() else []:
        entry, out = problems_of(folder)
        problems += out
        if entry and not out:
            entries.append(entry)
    return {"version": VERSION, "addons": entries}, problems


def main():
    data, problems = build()
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    for p in problems:
        print(f"::error::{p}" if "--check" in sys.argv else f"problem: {p}")
    if "--check" in sys.argv:
        have = LIST.read_text(encoding="utf-8") if LIST.exists() else ""
        if have != text:
            print("::error::addons.json is not up to date: run python3 tools/build_list.py and commit it")
            return 1
        return 1 if problems else 0
    LIST.write_text(text, encoding="utf-8")
    print(f"addons.json: {len(data['addons'])} add-ons")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
