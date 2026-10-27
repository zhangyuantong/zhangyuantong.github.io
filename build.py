#!/usr/bin/env python
"""Assemble the site.

Two jobs:

1. Fill the repeated blocks (aurora, nav, footer, post list) into the pages,
   from the files in partials/.

2. Turn posts/*.md into posts/<slug>/index.html.

    python build.py            write everything
    python build.py --check    exit 1 if anything is out of date

Articles are plain Markdown with a small front matter block:

    ---
    title: Traffic Jam for Snails
    date: 2025-10-19
    tags: brain-teaser, probability
    excerpt: One or two sentences for the list and for search engines.
    ---

    Body starts here.
"""

import html as html_mod
import re
import sys
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
PARTIALS = ROOT / "partials"
POSTS = ROOT / "posts"

PAGES = [
    "index.html",
    "404.html",
    "cv/index.html",
    "posts/index.html",
    "about/index.html",
]

NAV_ACTIVE = {
    "index.html": "about",
    "about/index.html": "about",
    "posts/index.html": "posts",
    "cv/index.html": "cv",
}

KATEX_HEAD = '<link rel="stylesheet" href="/assets/katex/katex.min.css">'
KATEX_SCRIPTS = (
    '<script src="/assets/katex/katex.min.js"></script>\n'
    '<script src="/assets/katex/auto-render.min.js"></script>'
)

MD = MarkdownIt("commonmark", {"html": False, "breaks": True})
for rule in ("table", "strikethrough"):
    try:
        MD.enable(rule)
    except Exception:
        pass

# Math is lifted out of the Markdown before parsing and put back afterwards,
# so that characters like < > * _ inside formulas survive untouched.
MATH_PATTERNS = [
    re.compile(r"\$\$[\s\S]+?\$\$"),
    re.compile(r"\\\[[\s\S]+?\\\]"),
    re.compile(r"(?<!\\)\$(?!\$)[^$\n]+?(?<!\\)\$"),
    re.compile(r"\\\([\s\S]+?\\\)"),
]


# ---------------------------------------------------------------- blocks


def indent_of(text, pos):
    line_start = text.rfind("\n", 0, pos) + 1
    return re.match(r"[ \t]*", text[line_start:]).group(0)


def has_block(text, name):
    return "<!-- %s:START -->" % name in text


def fill(text, name, body):
    """Replace everything between the START/END markers with body."""
    start = "<!-- %s:START -->" % name
    end = "<!-- %s:END -->" % name
    if start not in text:
        return text
    i = text.index(start)
    j = text.index(end) + len(end)
    ind = indent_of(text, i)
    body = body.rstrip("\n")
    if body:
        body = "\n".join((ind + line) if line.strip() else line for line in body.splitlines())
        new = "%s%s\n%s\n%s%s" % (ind, start, body, ind, end)
    else:
        new = "%s%s\n%s%s" % (ind, start, ind, end)
    line_start = text.rfind("\n", 0, i) + 1
    return text[:line_start] + new + text[j:]


def nav_key(rel):
    if rel in NAV_ACTIVE:
        return NAV_ACTIVE[rel]
    if rel.startswith("posts/"):
        return "posts"
    return ""


def render(rel, text, posts):
    text = fill(text, "AURORA", (PARTIALS / "aurora.html").read_text(encoding="utf-8"))
    text = fill(
        text,
        "NAV",
        (PARTIALS / "nav.html")
        .read_text(encoding="utf-8")
        .replace("{{cur_about}}", ' aria-current="page"' if nav_key(rel) == "about" else "")
        .replace("{{cur_posts}}", ' aria-current="page"' if nav_key(rel) == "posts" else "")
        .replace("{{cur_cv}}", ' aria-current="page"' if nav_key(rel) == "cv" else ""),
    )
    text = fill(text, "FOOTER", (PARTIALS / "footer.html").read_text(encoding="utf-8"))
    if has_block(text, "POSTLIST"):
        text = fill(text, "POSTLIST", build_post_list(posts))
    return text


# ---------------------------------------------------------------- posts


def parse_front_matter(text):
    if not text.startswith("---"):
        raise SystemExit("post is missing its front matter block")
    end = text.find("\n---", 3)
    if end == -1:
        raise SystemExit("post front matter is not closed with ---")

    meta = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        meta[key.strip().lower()] = value

    body = text[end + 4 :].lstrip("\n")
    return meta, body


def protect_math(text):
    saved = []

    def stash(match):
        saved.append(match.group(0))
        return "@@M%d@@" % (len(saved) - 1)

    for pattern in MATH_PATTERNS:
        text = pattern.sub(stash, text)
    return text, saved


def plain_text(markup):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", markup)).strip()


def reading_minutes(body_html):
    words = len(plain_text(body_html).split())
    return max(1, round(words / 200))


def load_post(path):
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    slug = path.stem

    for key in ("title", "date"):
        if key not in meta:
            raise SystemExit("%s: front matter needs a '%s'" % (path.name, key))

    protected, saved = protect_math(body)
    body_html = MD.render(protected)
    for i, chunk in enumerate(saved):
        # entities decode back to the original characters in the text node,
        # which keeps a bare < or & from being read as markup
        safe = chunk.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        body_html = body_html.replace("@@M%d@@" % i, safe)

    excerpt = meta.get("excerpt") or plain_text(body_html)[:157].rsplit(" ", 1)[0] + "…"
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]

    return {
        "slug": slug,
        "title": meta["title"],
        "date_iso": meta["date"],
        "date_text": meta["date"].replace("-", "."),
        "tags": tags,
        "excerpt": excerpt,
        "reading": meta.get("reading") or str(reading_minutes(body_html)),
        "body_html": body_html,
        "has_math": "$" in body or "\\(" in body or "\\[" in body,
    }


def render_post(post):
    tpl = (PARTIALS / "post.html").read_text(encoding="utf-8")
    tags_line = " · ".join(post["tags"])

    values = {
        "{{title}}": html_mod.escape(post["title"]),
        "{{excerpt}}": html_mod.escape(post["excerpt"], quote=True),
        "{{tags_attr}}": html_mod.escape(", ".join(post["tags"]), quote=True),
        "{{tags_line}}": html_mod.escape(tags_line),
        "{{date_iso}}": post["date_iso"],
        "{{date_text}}": post["date_text"],
        "{{reading}}": post["reading"],
        "{{katex_head}}": KATEX_HEAD if post["has_math"] else "",
        "{{katex_scripts}}": KATEX_SCRIPTS if post["has_math"] else "",
    }
    for key, value in values.items():
        tpl = tpl.replace(key, value)

    return fill(tpl, "BODY", post["body_html"])


def build_post_list(posts):
    if not posts:
        return ""
    row = (PARTIALS / "post-row.html").read_text(encoding="utf-8")
    rows = []
    for post in sorted(posts, key=lambda p: p["date_iso"], reverse=True):
        filled = (
            row.replace("{{href}}", "/posts/%s/" % post["slug"])
            .replace("{{date_iso}}", post["date_iso"])
            .replace("{{date_text}}", post["date_text"])
            .replace("{{title}}", html_mod.escape(post["title"]))
            .replace("{{excerpt}}", html_mod.escape(post["excerpt"]))
        )
        chips = "".join("<span>%s</span>" % html_mod.escape(t) for t in post["tags"])
        filled = filled.replace("{{tags}}", '<div class="tags">%s</div>' % chips if chips else "")
        rows.append(filled)
    return "\n\n".join(rows)


# ---------------------------------------------------------------- main


def collect():
    posts = [load_post(p) for p in sorted(POSTS.glob("*.md"))]
    for post in posts:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", post["date_iso"]):
            raise SystemExit("posts/%s.md: date must look like 2025-10-19" % post["slug"])

    stale_dirs = [
        d.name
        for d in POSTS.iterdir()
        if d.is_dir() and (d / "index.html").exists() and not (POSTS / (d.name + ".md")).exists()
    ]
    if stale_dirs:
        print(
            "warning: generated folders with no source left behind: %s" % ", ".join(stale_dirs),
            file=sys.stderr,
        )

    outputs = {}
    for rel in PAGES:
        path = ROOT / rel
        if not path.exists():
            raise SystemExit("missing page: %s" % rel)
        outputs[path] = render(rel, path.read_text(encoding="utf-8"), posts)

    for post in posts:
        rel = "posts/%s/index.html" % post["slug"]
        outputs[ROOT / rel] = render(rel, render_post(post), posts)

    return outputs


def main():
    check = "--check" in sys.argv
    stale = []

    for path, content in sorted(collect().items()):
        rel = path.relative_to(ROOT).as_posix()
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        if check:
            stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            print("wrote %s" % rel)

    if check and stale:
        print("out of date: %s" % ", ".join(stale), file=sys.stderr)
        print("run: python build.py", file=sys.stderr)
        return 1

    if not check:
        print("build complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
