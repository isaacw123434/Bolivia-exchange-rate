import json
import re
import sys
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://boliviatravelmoney.site"
LANG_PATHS = {
    "en": "",
    "es": "es",
    "pt": "pt",
    "he": "he",
    "fr": "fr",
    "de": "de",
    "ko": "ko",
    "zh-CN": "zh-CN",
}


def fail(message):
    print(f"FAIL: {message}")
    return False


def read_json(path):
    with (ROOT / path).open(encoding="utf-8") as f:
        return json.load(f)


def page_path(lang, page=""):
    parts = []
    if LANG_PATHS[lang]:
        parts.append(LANG_PATHS[lang])
    if page:
        parts.append(page)
    return ROOT.joinpath(*parts, "index.html") if parts else ROOT / "index.html"


def canonical_url(lang, page=""):
    parts = []
    if LANG_PATHS[lang]:
        parts.append(LANG_PATHS[lang])
    if page:
        parts.append(page)
    return BASE_URL + "/" + ("/".join(parts) + "/" if parts else "")


def official_usd_to_bob(rates):
    official = rates["official_rates"]
    return official["BOB"] / official["USD"]


def check_history(rates, history):
    ok = True
    if len(history) < 30:
        ok = fail(f"expected at least 30 history points, found {len(history)}")
    dates = [item.get("date") for item in history]
    if dates != sorted(dates):
        ok = fail("data/history.json dates must be sorted ascending")
    if len(dates) != len(set(dates)):
        ok = fail("data/history.json contains duplicate dates")

    latest_rate_date = datetime.fromisoformat(rates["date"]).date().isoformat()
    if history[-1]["date"] != latest_rate_date:
        ok = fail(f"latest history date {history[-1]['date']} does not match rates date {latest_rate_date}")

    for item in history:
        street = item.get("street_rate_bob")
        official = item.get("official_usd_bob")
        premium = item.get("street_premium_pct")
        if not isinstance(street, (int, float)) or not isinstance(official, (int, float)) or not isinstance(premium, (int, float)):
            ok = fail(f"invalid numeric history row for {item.get('date')}")
            break
        expected = round(((street / official) - 1) * 100, 2)
        if abs(expected - premium) > 0.02:
            ok = fail(f"premium mismatch for {item['date']}: expected {expected}, got {premium}")
            break
    return ok


def check_pages(translations, rates, history):
    ok = True
    street_display = f"{float(rates['street_rate_bob']):.2f} BOB"
    official_display = f"{official_usd_to_bob(rates):.2f} BOB"
    premium_display = f"{((rates['street_rate_bob'] / official_usd_to_bob(rates)) - 1) * 100:.1f}%"

    for lang, trans in translations.items():
        for file_path in (page_path(lang), page_path(lang, "history")):
            if not file_path.exists():
                ok = fail(f"missing generated page {file_path.relative_to(ROOT)}")
                continue
            html = file_path.read_text(encoding="utf-8")
            if "\ufffd" in html:
                ok = fail(f"replacement character found in {file_path.relative_to(ROOT)}")
            if "<title>" not in html or '<meta name="description"' not in html:
                ok = fail(f"missing title or description in {file_path.relative_to(ROOT)}")
            for match in re.findall(r'src="/static/flags/([^"]+\.svg)"', html):
                if not (ROOT / "static" / "flags" / match).exists():
                    ok = fail(f"missing flag asset {match} referenced by {file_path.relative_to(ROOT)}")

        home_html = page_path(lang).read_text(encoding="utf-8")
        for text in (trans["meta_title"], trans["today_rates_title"], street_display, official_display, premium_display):
            if text not in home_html:
                ok = fail(f"homepage {lang} missing expected text: {text}")

        history_html = page_path(lang, "history").read_text(encoding="utf-8")
        for date_text in (history[0]["date"], history[-1]["date"]):
            if date_text not in history_html:
                ok = fail(f"history page {lang} missing date {date_text}")

    return ok


def check_sitemap():
    ok = True
    sitemap = ROOT / "sitemap.xml"
    tree = ET.parse(sitemap)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [node.text for node in tree.findall(".//sm:loc", ns)]
    expected = []
    for lang in LANG_PATHS:
        expected.append(canonical_url(lang))
        expected.append(canonical_url(lang, "history"))

    if sorted(locs) != sorted(expected):
        ok = fail(f"sitemap URLs differ from expected set: found {len(locs)}, expected {len(expected)}")
    if any("/rates/" in loc for loc in locs):
        ok = fail("sitemap should not include /rates/ URLs")
    return ok


def check_generated_source():
    ok = True
    app_js = (ROOT / "js" / "app.js").read_text(encoding="utf-8")
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    for identifier in [
        "lang-selector-button",
        "lang-selector-menu",
        "bill-amount",
        "results-list",
        "winner-card-container",
    ]:
        if identifier not in template:
            ok = fail(f"template missing #{identifier}")
    for snippet in ["function calculate()", "function fetchRates()", "function updateLanguageSelector"]:
        if snippet not in app_js:
            ok = fail(f"app.js missing {snippet}")
    return ok


def main():
    translations = read_json("translations.json")
    rates = read_json("data/rates.json")
    history = read_json("data/history.json")

    checks = [
        check_history(rates, history),
        check_pages(translations, rates, history),
        check_sitemap(),
        check_generated_source(),
    ]

    if all(checks):
        print("Site verification passed.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
