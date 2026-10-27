#!/usr/bin/env python
"""Assemble the repeated parts of the site.

Everything that appears on more than one page lives in partials/ and is
pasted in here between HTML markers:

    <!-- AURORA:START -->   ... <!-- AURORA:END -->
    <!-- NAV:START -->      ... <!-- NAV:END -->
    <!-- FOOTER:START -->   ... <!-- FOOTER:END -->
    <!-- POSTLIST:START --> ... <!-- POSTLIST:END -->   (posts/index.html only)

The post list is derived from the post pages themselves, so a new article
shows up in the list without anyone touching the index.

    python build.py            write the generated blocks
    python build.py --check    exit 1 if any page is out of date
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTIALS = ROOT / "partials"

# page -> which nav item is the current one
NAV_ACTIVE = {
    "index.html": "about",
    "about/index.html": "about",
    "posts/index.html": "posts",
    "cv/index.html": "cv",
}
# posts/*/index.html are all "posts"
POSTS_DIR = ROOT / "posts"

TIME_RE = re.compile(r'<time datetime="([\d-]+)">([^<]+)</time>')
TITLE_RE = re.compile(r'<section class="article-head wrap">.*?<h1>(.*?)</h1>', re.S)
DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"')
TAGS_RE = re.compile(r'<meta name="post:tags" content="([^"]*)"')
H1_LINE_RE = re.compile(r'^[ \t]*<h1>.*?</h1>\s*$', re.M)


def pages():
    return sorted(set(ROOT.glob("*.html")) | set(ROOT.glob("*/index.html")) | set(ROOT.glob("*/*/index.html")))


def nav_key(rel):
    if rel in NAV_ACTIVE:
        return NAV_ACTIVE[rel]
    if rel.startswith("posts/"):
        return "posts"
    return ""


def indent_of(text, pos):
    line_start = text.rfind("\n", 0, pos) + 1
    return re.match(r"[ \t]*", text[line_start:]).group(0)


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


def has_block(text, name):
    return "<!-- %s:START -->" % name in text


def post_meta(path):
    html = path.read_text(encoding="utf-8")
    time_m = TIME_RE.search(html)
    title_m = TITLE_RE.search(html)
    desc_m = DESC_RE.search(html)
    tags_m = TAGS_RE.search(html)
    missing = [
        label
        for label, match in (
            ('<time datetime="...">', time_m),
            ("<h1> in .article-head", title_m),
            ('<meta name="description">', desc_m),
        )
        if not match
    ]
    if missing:
        raise SystemExit("%s is missing: %s" % (path.relative_to(ROOT), ", ".join(missing)))

    tags = []
    if tags_m:
        tags = [t.strip() for t in tags_m.group(1).split(",") if t.strip()]

    return {
        "date_iso": time_m.group(1),
        "date_text": time_m.group(2).strip(),
        "title": title_m.group(1).strip(),
        "excerpt": desc_m.group(1).strip(),
        "tags": tags,
        "href": "/posts/%s/" % path.parent.name,
    }


def post_row(post):
    row = (PARTIALS / "post-row.html").read_text(encoding="utf-8")
    tag_html = ""
    if post["tags"]:
        chips = "".join("<span>%s</span>" % t for t in post["tags"])
        tag_html = '<div class="tags">%s</div>' % chips
    return (
        row.replace("{{href}}", post["href"])
        .replace("{{date_iso}}", post["date_iso"])
        .replace("{{date_text}}", post["date_text"])
        .replace("{{title}}", post["title"])
        .replace("{{excerpt}}", post["excerpt"])
        .replace("{{tags}}", tag_html)
    )


def build_posts_list():
    posts = [post_meta(p) for p in POSTS_DIR.glob("*/index.html")]
    if not posts:
        return ""
    posts.sort(key=lambda p: p["date_iso"], reverse=True)
    return "\n".join(post_row(p) for p in posts)


def render(rel, text):
    text = fill(text, "AURORA", PARTIALS.joinpath("aurora.html").read_text(encoding="utf-8"))
    text = fill(text, "NAV", PARTIALS.joinpath("nav.html").read_text(encoding="utf-8")
                .replace("{{cur_about}}", ' aria-current="page"' if nav_key(rel) == "about" else "")
                .replace("{{cur_posts}}", ' aria-current="page"' if nav_key(rel) == "posts" else "")
                .replace("{{cur_cv}}", ' aria-current="page"' if nav_key(rel) == "cv" else ""))
    text = fill(text, "FOOTER", PARTIALS.joinpath("footer.html").read_text(encoding="utf-8"))
    if has_block(text, "POSTLIST"):
        text = fill(text, "POSTLIST", build_posts_list())
    return text


def main():
    check = "--check" in sys.argv
    stale = []

    for path in pages():
        rel = path.relative_to(ROOT).as_posix()
        original = path.read_text(encoding="utf-8")
        updated = render(rel, original)
        if updated == original:
            continue
        if check:
            stale.append(rel)
        else:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print("updated %s" % rel)

    if check and stale:
        print("out of date: %s" % ", ".join(stale), file=sys.stderr)
        print("run: python build.py", file=sys.stderr)
        return 1

    if not check:
        print("build complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
