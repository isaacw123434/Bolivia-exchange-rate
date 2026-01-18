import json
import os
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Configuration
BASE_URL = "https://boliviatravelmoney.site"
TEMPLATE_FILE = "template.html"
TRANSLATIONS_FILE = "translations.json"
OUTPUT_DIR = "."

def main():
    # Load translations
    with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(TEMPLATE_FILE)

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

        # Prepare context
        context = {
            "lang_code": lang_code,
            "current_date": current_date,
            "current_date_long": current_date_long,
            "date_modified": now_iso,
            "canonical_url": f"{BASE_URL}/" if lang_code == 'en' else f"{BASE_URL}/{lang_code}/",
            "languages": languages_list,
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
        sitemap_content += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE_URL}/"/>\n'
        sitemap_content += '  </url>\n'

    sitemap_content += '</urlset>'

    with open("sitemap.xml", "w", encoding='utf-8') as f:
        f.write(sitemap_content)
    print("Sitemap generated.")

if __name__ == "__main__":
    main()
