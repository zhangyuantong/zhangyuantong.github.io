# zhangyuantong.github.io

Personal site. Plain HTML, one stylesheet, one script, and a 150-line build
script. No template engine, no dependencies, no framework — the HTML in this
repo is exactly what the browser gets.

## File map

| What you want to change | Which file |
|---|---|
| Homepage copy, subtitle, photo, links | `index.html` |
| CV | `cv/index.html` |
| Post list | generated — see below |
| One article | `posts/<slug>/index.html` |
| Nav bar, footer, page glow | `partials/nav.html`, `partials/footer.html`, `partials/aurora.html` |
| Colours, type, spacing, motion | `assets/style.css` (colour variables at the top) |
| Behaviour | `assets/main.js` |
| Build | `build.py` |
| 404 page | `404.html` |

## How the repeated parts work

Anything that appears on more than one page lives in `partials/` and is pasted
in by `build.py` between markers:

```html
<!-- AURORA:START -->
...generated...
<!-- AURORA:END -->
```

So the nav is written once, in `partials/nav.html`, and the background glow once,
in `partials/aurora.html`. To change either, edit that file and run:

```sh
python build.py
```

The post list is generated the same way. It is read out of the articles
themselves — each post's `<time>`, `<h1>`, `<meta name="description">` and
`<meta name="post:tags">` — so there is no second place to keep in sync.

**You cannot forget to run it.** A pre-commit hook runs `python build.py
--check` and refuses the commit if anything is stale. Enable it once per clone:

```sh
git config core.hooksPath .githooks
```

## Changing text

Open the `.html` in any editor. Places you are likely to touch are marked with
a comment you can search for — type `EDIT:` in the find box:

```html
<!-- EDIT: subtitle -->
<p class="tagline">Trader by trade, researcher by habit, coder by compulsion.</p>
```

Markers exist in `index.html` for kicker, headline, subtitle, body, links and
photo.

Do not edit inside a `START` / `END` marker pair — `build.py` overwrites it.

## Adding a post

1. Make a folder `posts/<slug>/`, e.g. `posts/hurst/`
2. Copy `posts/snail/index.html` into it
3. Change the title, `<time datetime="2025-10-19">2025.10.19</time>`, the
   `<h1>`, `<meta name="description">` and `<meta name="post:tags">`
4. Write the body inside `<article class="article-body wrap">`
5. Run `python build.py`

The list on `/posts/` updates by itself, newest first.

Maths works out of the box: write `$...$` inline or `$$...$$` on its own line
and KaTeX renders it. If a page has no maths, delete the first two `<script>`
tags at the bottom (`katex.min.js`, `auto-render.min.js`) to make it lighter.

## Deleting a post

Delete the folder `posts/<slug>/` and run `python build.py`.

## Changing the palette

Top of `assets/style.css`:

```css
:root {
  --bg:   #0a0a0c;   /* page background */
  --ink:  #e9e7e2;   /* body text */
  --gold: #d6ac63;   /* accent: links, rules, highlights */
  ...
}
```

Changing `--gold` alone recolours the whole site. For a light theme, set `--bg`
to `#fbfaf8`, `--ink` to `#17171a`, and change `--line` from white to black
(`rgba(0,0,0,.08)`).

## Running it locally

The site uses absolute paths (`/assets/style.css`), so it needs a server rather
than a double-click:

```sh
python -m http.server 8000
```

Then open <http://localhost:8000>.

## If it feels slow

Rendering happens in your own browser, so where the site is hosted makes no
difference to smoothness.

To strip a page to bare content, give its `<html>` tag a `lite` class:

```html
<html lang="en" class="lite">
```

That removes the ambient glow, the grain, the pointer light and every entrance
animation. It has to be added per file, because it sits outside the NAV and
FOOTER markers.

## Publishing

```sh
python build.py
git add -A
git commit -m "what you changed"
git push
```

GitHub Pages rebuilds in about a minute. There is no server-side build.

## Layout

```
index.html              homepage / about
cv/index.html           CV
posts/index.html        post list (generated block inside)
posts/<slug>/index.html one folder per article
about/index.html        old /about/ link, redirects home
404.html
partials/nav.html       the nav, written once
partials/footer.html    the footer, written once
partials/aurora.html    the background glow, written once
partials/post-row.html  template for one row of the post list
build.py                pastes the partials in and builds the post list
.githooks/pre-commit    refuses a commit when the build is stale
assets/style.css        all styling
assets/main.js          all behaviour
assets/katex/           KaTeX, vendored (no CDN)
assets/about_photo.jpg  homepage photo
```
