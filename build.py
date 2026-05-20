import json
import os
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Configuration
BASE_URL = "https://boliviatravelmoney.site"
TEMPLATE_FILE = "template.html"
DATA_PAGE_TEMPLATE_FILE = "data-page.html"
TRANSLATIONS_FILE = "translations.json"
OUTPUT_DIR = "."

PAGE_SLUGS = ("history",)

def main():
    # Load translations
    with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(TEMPLATE_FILE)
    data_page_template = env.get_template(DATA_PAGE_TEMPLATE_FILE)
    rate_context = build_rate_context()

# Locale Data
    LOCALE_DATA = {
        'en': {
            'months_short': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'months_long': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            'days_long': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        },
        'es': {
            'months_short': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            'months_long': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            'days_long': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        },
        'pt': {
            'months_short': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            'months_long': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
            'days_long': ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        },
        'fr': {
            'months_short': ['Janv.', 'Févr.', 'Mars', 'Avril', 'Mai', 'Juin', 'Juil.', 'Août', 'Sept.', 'Oct.', 'Nov.', 'Déc.'],
            'months_long': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
            'days_long': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        },
        'de': {
            'months_short': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
            'months_long': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
            'days_long': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        },
        'zh-CN': {
            'months_short': ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
            'months_long': ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
            'days_long': ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        },
        'ko': {
            'months_short': ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
            'months_long': ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
            'days_long': ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        },
        'he': {
            'months_short': ['ינו', 'פבר', 'מרץ', 'אפר', 'מאי', 'יוני', 'יולי', 'אוג', 'ספט', 'אוק', 'נוב', 'דצמ'],
            'months_long': ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'],
            'days_long': ['יום שני', 'יום שלישי', 'יום רביעי', 'יום חמישי', 'יום שישי', 'יום שבת', 'יום ראשון']
        }
    }

    # Prepare languages list for hreflang
    languages_list = []
    for code in translations.keys():
        url = f"{BASE_URL}/" if code == 'en' else f"{BASE_URL}/{code}/"
        languages_list.append({
            "code": code,
            "url": url
        })

    # Generate pages
    sitemap_urls = []
    now = datetime.now()
    now_iso = now.astimezone().isoformat()

    for lang_code, trans_data in translations.items():
        print(f"Generating {lang_code}...")

        # Localize date
        locale = LOCALE_DATA.get(lang_code, LOCALE_DATA['en'])

        day = now.day
        month_idx = now.month - 1
        year = now.year
        weekday_idx = now.weekday()

        short_month = locale['months_short'][month_idx]
        long_month = locale['months_long'][month_idx]
        long_day = locale['days_long'][weekday_idx]

        # Use format strings from translations.json, fallback to defaults if missing
        date_short_fmt = trans_data.get('date_short', "{day} {short_month} {year}")
        date_long_fmt = trans_data.get('date_long', "{long_day}, {long_month} {day}, {year}")

        current_date = date_short_fmt.format(
            day=day,
            short_month=short_month,
            year=year,
            long_day=long_day,
            long_month=long_month
        )

        current_date_long = date_long_fmt.format(
            day=day,
            short_month=short_month,
            year=year,
            long_day=long_day,
            long_month=long_month
        )

        home_url = f"{BASE_URL}/" if lang_code == 'en' else f"{BASE_URL}/{lang_code}/"

        # Prepare context
        context = {
            "lang_code": lang_code,
            "current_date": current_date,
            "current_date_long": current_date_long,
            "date_modified": now_iso,
            "canonical_url": home_url,
            "languages": languages_list,
            "home_url": home_url,
            "history_page_url": page_url(lang_code, "history"),
            **rate_context,
            **trans_data  # Unpack translations
        }

        # Render
        html_content = template.render(context)

        # Output path
        if lang_code == 'en':
            output_path = os.path.join(OUTPUT_DIR, "index.html")
        else:
            dir_path = os.path.join(OUTPUT_DIR, lang_code)
            os.makedirs(dir_path, exist_ok=True)
            output_path = os.path.join(dir_path, "index.html")

        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Add to sitemap list
        sitemap_urls.append({
            "loc": context["canonical_url"],
            "lastmod": datetime.now().strftime("%Y-%m-%d"),
            "alternates": languages_list
        })

        # Generate shareable data pages
        for page_kind in PAGE_SLUGS:
            page_languages = [
                {
                    "code": alt_code,
                    "url": page_url(alt_code, page_kind)
                }
                for alt_code in translations.keys()
            ]
            page_context = {
                **context,
                "canonical_url": page_url(lang_code, page_kind),
                "languages": page_languages,
                "x_default_url": page_url("en", page_kind),
                "page_kind": page_kind,
                "page_title": trans_data[f"{page_kind}_page_title"],
                "page_description": trans_data[f"{page_kind}_page_description"],
                "page_intro": trans_data[f"{page_kind}_page_intro"],
                "history_points": build_history_points(rate_context),
            }
            page_html = data_page_template.render(page_context)
            page_output_path = output_path_for_page(lang_code, page_kind)
            os.makedirs(os.path.dirname(page_output_path), exist_ok=True)
            with open(page_output_path, 'w', encoding='utf-8') as f:
                f.write(page_html)

            sitemap_urls.append({
                "loc": page_context["canonical_url"],
                "lastmod": datetime.now().strftime("%Y-%m-%d"),
                "alternates": page_languages,
                "x_default": page_url("en", page_kind)
            })

    # Generate Sitemap
    generate_sitemap(sitemap_urls)
    print("Build complete.")

def generate_sitemap(urls):
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'

    for url_data in urls:
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{url_data["loc"]}</loc>\n'
        sitemap_content += f'    <lastmod>{url_data["lastmod"]}</lastmod>\n'
        for alt in url_data["alternates"]:
            sitemap_content += f'    <xhtml:link rel="alternate" hreflang="{alt["code"]}" href="{alt["url"]}"/>\n'
        # Also add x-default
        sitemap_content += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url_data.get("x_default", BASE_URL + "/")}"/>\n'
        sitemap_content += '  </url>\n'

    sitemap_content += '</urlset>'

    with open("sitemap.xml", "w", encoding='utf-8') as f:
        f.write(sitemap_content)
    print("Sitemap generated.")

def page_url(lang_code, slug):
    if lang_code == 'en':
        return f"{BASE_URL}/{slug}/"
    return f"{BASE_URL}/{lang_code}/{slug}/"

def output_path_for_page(lang_code, slug):
    if lang_code == 'en':
        return os.path.join(OUTPUT_DIR, slug, "index.html")
    return os.path.join(OUTPUT_DIR, lang_code, slug, "index.html")

def build_rate_context():
    with open(os.path.join("data", "rates.json"), 'r', encoding='utf-8') as f:
        rates = json.load(f)

    official_rates = rates.get("official_rates", {})
    street_rate = float(rates.get("street_rate_bob") or 0)
    base_to_usd = float(official_rates.get("USD") or 1)
    base_to_bob = float(official_rates.get("BOB") or 0)
    official_usd_bob = base_to_bob / base_to_usd if base_to_usd and base_to_bob else 0
    street_premium = ((street_rate / official_usd_bob) - 1) * 100 if official_usd_bob else 0

    updated = rates.get("date")
    try:
        updated_dt = datetime.fromisoformat(updated)
        updated_display = updated_dt.strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError):
        updated_display = updated or "Unknown"

    context = {
        "street_rate": street_rate,
        "official_usd_bob": official_usd_bob,
        "street_premium": street_premium,
        "street_rate_display": f"{street_rate:.2f} BOB",
        "official_usd_bob_display": f"{official_usd_bob:.2f} BOB",
        "street_premium_display": f"{street_premium:.1f}%",
        "rates_updated_display": updated_display,
        "history_source_points": load_history_points(street_rate, official_usd_bob, street_premium, updated_display)
    }
    return context

def load_history_points(street_rate, official_usd_bob, street_premium, updated_display):
    history_path = os.path.join("data", "history.json")
    if not os.path.exists(history_path):
        return [{
            "date": updated_display.split(" ")[0],
            "street": street_rate,
            "official": official_usd_bob,
            "premium": street_premium
        }]

    with open(history_path, 'r', encoding='utf-8') as f:
        history = json.load(f)

    points = []
    for entry in history:
        street = float(entry.get("street_rate_bob") or 0)
        official = float(entry.get("official_usd_bob") or 0)
        if not entry.get("date") or not street or not official:
            continue
        premium = float(entry.get("street_premium_pct") or ((street / official) - 1) * 100)
        points.append({
            "date": entry["date"],
            "street": street,
            "official": official,
            "premium": premium
        })

    return sorted(points, key=lambda item: item["date"], reverse=True)

def build_history_points(rate_context):
    points = []
    for point in rate_context["history_source_points"]:
        width = max(8, min(100, point["premium"]))
        points.append({
            "date": point["date"],
            "street": f'{point["street"]:.2f} BOB',
            "official": f'{point["official"]:.2f} BOB',
            "premium": f'{point["premium"]:.1f}%',
            "width": f"{width:.1f}",
        })
    return points

if __name__ == "__main__":
    main()
