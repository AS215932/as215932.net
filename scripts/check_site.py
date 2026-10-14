#!/usr/bin/env python3
"""Static checks for the as215932.net site (stdlib only).

- every HTML page parses with balanced block tags and has a <title>
- no duplicate id attributes on a page
- every local href/src resolves to a file served by deploy.sh
  (/ -> index.html, /foo -> foo.html, /style.css), and #fragments exist
- with --external, every http(s) link answers < 400 (HEAD, then GET)
"""
from __future__ import annotations

import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
CHECKED = {"html", "head", "body", "div", "section", "main", "nav", "header", "footer", "table", "ul", "ol", "pre"}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, int]] = []
        self.ids: list[str] = []
        self.stack: list[tuple[str, int]] = []
        self.errors: list[str] = []
        self.title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line = self.getpos()[0]
        if tag == "title":
            self.title = True
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append((value, line))
            if name == "id" and value:
                self.ids.append(value)
        if tag in CHECKED:
            self.stack.append((tag, line))

    def handle_endtag(self, tag: str) -> None:
        if tag not in CHECKED or tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.errors.append(f"line {self.getpos()[0]}: unexpected </{tag}>")
            return
        self.stack.pop()


def local_target(path: str) -> Path | None:
    if path in ("", "/"):
        return ROOT / "index.html"
    name = path.lstrip("/")
    if name.endswith((".css", ".html")):
        return ROOT / name
    return ROOT / f"{name}.html"


def external_ok(url: str) -> str | None:
    headers = {"User-Agent": "as215932.net-linkcheck"}
    for method in ("HEAD", "GET"):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method=method, headers=headers), timeout=20):
                return None
        except urllib.error.HTTPError as exc:
            if method == "GET":
                return f"HTTP {exc.code}"
        except OSError as exc:
            if method == "GET":
                return str(exc)
    return None


def main() -> int:
    external = "--external" in sys.argv
    pages = {p: Page() for p in sorted(ROOT.glob("*.html"))}
    for path, page in pages.items():
        page.feed(path.read_text(encoding="utf-8"))
        page.close()
    problems: list[str] = []
    seen_external: set[str] = set()
    for path, page in pages.items():
        name = path.name
        problems += [f"{name}: {e}" for e in page.errors]
        problems += [f"{name}: <{t}> opened on line {ln} is never closed" for t, ln in page.stack]
        if not page.title:
            problems.append(f"{name}: missing <title>")
        dupes = {i for i in page.ids if page.ids.count(i) > 1}
        problems += [f"{name}: duplicate id {i!r}" for i in sorted(dupes)]
        for link, line in page.links:
            if link.startswith(("mailto:", "tel:")):
                continue
            if link.startswith(("http://", "https://")):
                seen_external.add(link)
                continue
            target_path, _, fragment = link.partition("#")
            target = path if not target_path else local_target(target_path)
            if target is None or not target.is_file():
                problems.append(f"{name}:{line}: broken local link {link!r}")
                continue
            if fragment and target in pages and fragment not in pages[target].ids:
                problems.append(f"{name}:{line}: missing anchor {link!r}")
    if external:
        for url in sorted(seen_external):
            err = external_ok(url)
            if err:
                problems.append(f"external link {url}: {err}")
    for p in problems:
        print(p)
    print(f"checked {len(pages)} pages, {len(seen_external)} external links ({'checked' if external else 'skipped'})")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
