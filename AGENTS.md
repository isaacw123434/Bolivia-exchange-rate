# Agent Guide

## Project Overview

This repository is a static, multilingual travel-money calculator for comparing Bolivia street USD exchange, money-transfer-app rates, and card exchange rates. The site is served from committed static files and updated by a scheduled GitHub Actions scraper.

Key runtime files:

- `index.html` and `*/index.html` are generated localized pages.
- `template.html` is the Jinja2 source template for generated HTML.
- `translations.json` contains all localized UI/content strings.
- `js/app.js` contains the browser calculator, rate loading, language redirect, theme state, and localStorage cache behavior.
- `data/rates.json` is the committed exchange-rate payload consumed by the frontend.
- `static/output.css` is generated Tailwind CSS.
- `sw.js` caches app assets and applies stale-while-revalidate behavior for `rates.json`.

## Local Setup

Install Node dependencies:

```powershell
npm install
```

Create and use a local Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Serve locally as a static site:

```powershell
python -m http.server
```

Then open `http://localhost:8000/`.

## Build And Update Commands

Build Tailwind CSS:

```powershell
npm run build:css
```

Generate localized HTML and `sitemap.xml` from `template.html` and `translations.json`:

```powershell
.\.venv\Scripts\python.exe build.py
```

Fetch rates and update `data/rates.json`:

```powershell
.\.venv\Scripts\python.exe scripts\scraper.py
```

The scraper uses `requests` for the street rate and `pyppeteer` for Monzo rate scraping. It can fall back to cached values from `data/rates.json` when external fetches fail.

## Verification

Check translation key coverage:

```powershell
.\.venv\Scripts\python.exe scripts\verify_translations.py
```

Important: `scripts/verify_translations.py` prints missing-key failures but currently does not exit with a nonzero status for missing keys. Read its output instead of trusting exit code alone.

There is no useful npm test suite yet. `npm test` is the default placeholder and exits with an error.

Before handing off meaningful frontend changes, run at least:

```powershell
npm run build:css
.\.venv\Scripts\python.exe scripts\verify_translations.py
.\.venv\Scripts\python.exe build.py
```

For UI changes, also serve the site locally and inspect the affected language/page in a browser.

## Generated Files And Editing Rules

- Prefer editing `template.html`, `translations.json`, `src/input.css`, and `js/app.js` rather than hand-editing generated localized HTML.
- After changes to `template.html` or `translations.json`, run `build.py` and include the generated `index.html`, language `index.html` files, and `sitemap.xml` changes if they are intentional.
- After changes to Tailwind classes or `src/input.css`, run `npm run build:css` and include `static/output.css` if it changed.
- Keep `data/rates.json` changes intentional. It is normally updated by `scripts/scraper.py` or the daily GitHub Action.
- Avoid relying on `npm test`; use the focused commands above.

## GitHub Actions

`.github/workflows/daily_scrape.yml` runs daily at 12:00 UTC and can also be triggered manually. It installs Python dependencies, runs `scripts/scraper.py`, runs `build.py`, then commits changes to:

- `data/rates.json`
- `index.html`
- `sitemap.xml`
- `*/index.html`

## Known Repository Notes

- The committed JavaScript and Python files contain some mojibake-looking non-ASCII text for localized labels, symbols, and flags. Do not normalize or rewrite those sections unless the task is specifically about encoding/localization cleanup.
- `npm install` currently reports two dependency audit findings in the Tailwind/dev toolchain. Treat audit fixes as a separate dependency-maintenance task unless requested.
