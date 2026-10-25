"""Scan top-level deck folders and write decks.json for the Lobby page."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

SKIP = re.compile(r"^(\.|_|assets?$|node_modules$|images?$|img$|css$|js$|fonts?$|lib$)", re.I)


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            a = dict(attrs)
            if a.get("name"):
                self.meta.setdefault(a["name"].lower(), a.get("content") or "")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def parse(html: str, folder: str) -> dict:
    p = HeadParser()
    p.feed(html)
    raw = p.title.strip() or folder
    parts = [s.strip() for s in re.split(r"[｜|]", raw)]
    title = parts[0]
    sub = parts[1] if len(parts) > 1 else ""
    tags = p.meta.get("tags") or p.meta.get("keywords") or ""
    if tags:
        tags = [s.strip() for s in re.split(r"[,，、]", tags) if s.strip()]
    elif sub:
        tag = re.sub(r"\s*第.+?[堂節課].*$", "", sub).strip()
        tags = [tag] if tag else []
    else:
        tags = []
    return {"name": folder, "title": title, "sub": sub, "tags": tags, "date": p.meta.get("date", "")}


def main():
    decks = [
        parse((d / "index.html").read_text(encoding="utf-8"), d.name)
        for d in sorted(Path(".").iterdir(), key=lambda x: x.name)
        if d.is_dir() and not SKIP.match(d.name) and (d / "index.html").exists()
    ]
    Path("decks.json").write_text(
        json.dumps(decks, ensure_ascii=False, indent=4) + "\n", encoding="utf-8"
    )
    print(f"decks.json: {len(decks)} decks")


if __name__ == "__main__":
    main()
