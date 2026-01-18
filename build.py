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

    # Common data
    current_date = datetime.now().strftime("%d %b %Y")
    current_date_long = datetime.now().strftime("%A, %B %d, %Y")

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

    for lang_code, trans_data in translations.items():
        print(f"Generating {lang_code}...")

        # Prepare context
        context = {
            "lang_code": lang_code,
            "current_date": current_date,
            "current_date_long": current_date_long,
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
