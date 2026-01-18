import requests
import json
import sys
import os
from datetime import datetime, timezone
import time
import asyncio
import re
from pyppeteer import launch

# Target Configuration
DOLARAPI_URL = "https://bo.dolarapi.com/v1/dolares/binance"
MONZO_BASE_URL = "https://monzo.com/currency-converter"

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

def get_street_rate():
    """
    Fetches the street rate (dolar blue) from dolarapi.com.
    """
    print(f"Fetching street rate from {DOLARAPI_URL}...")
    try:
        response = requests.get(DOLARAPI_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()

        # We use the 'venta' rate as it represents the street price
        if 'venta' in data and data['venta'] is not None:
            rate = float(data['venta'])
            print(f"Found street rate: {rate}")
            return rate
        else:
            print("Could not find 'venta' rate in API response.")
            return None

    except Exception as e:
        print(f"Error fetching street rate: {e}")
        return None

async def get_monzo_rates():
    print("Launching browser for Monzo scraping...")
    results = {}
    browser = None
    try:
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()

        print("Navigating to https://monzo.com/ecb-rates ...")
        await page.goto('https://monzo.com/ecb-rates', {'waitUntil': 'networkidle0'})

        print("Finding select element...")
        selects = await page.querySelectorAll('select')
        # The second select is typically the currency switcher
        if len(selects) < 2:
            print("Error: Could not find currency select element.")
            return None

        currency_select = selects[1]

        # Get available currencies
        options_handle = await currency_select.querySelectorAll('option')
        available_currencies = []
        for opt in options_handle:
            val = await page.evaluate('(element) => element.value', opt)
            available_currencies.append(val)

        print(f"Found {len(available_currencies)} currencies available.")

        # Base is GBP
        results['GBP'] = 1.0

        # Target currencies: USD, EUR, AUD, CAD, TWD, JPY, CNY, RUB, BOB, NZD, CHF, SGD, HKD, SEK, NOK, DKK, MXN, KRW, ILS
        # We also need these to be in the final 'official_rates' map.
        target_currencies = [
            'USD', 'EUR', 'AUD', 'CAD', 'TWD', 'JPY', 'CNY', 'RUB', 'BOB',
            'NZD', 'CHF', 'SGD', 'HKD', 'SEK', 'NOK', 'DKK', 'MXN', 'KRW', 'ILS'
        ]

        for currency in target_currencies:
            if currency not in available_currencies:
                print(f"Warning: Currency {currency} not found in Monzo dropdown.")
                continue

            print(f"Selecting {currency}...")

            # Select the option
            try:
                await page.select('select[role="listbox"]', currency)
            except Exception:
                 # Fallback to class if role selector fails
                 print("Fallback to class selector...")
                 await page.select('select.Select_input__JYjsP', currency)

            # Retry loop for finding the rate
            found_rate = False
            for attempt in range(3):
                # Wait for update.
                await asyncio.sleep(2.0)

                text_content = await page.evaluate('document.body.innerText')

                # We want the Mastercard Rate.
                # Format: "Mastercard Rate\n1 GBP = X CURRENCY"
                pattern = f"Mastercard Rate.*?1 GBP = ([0-9.]+)\\s+{currency}"
                match = re.search(pattern, text_content, re.DOTALL)

                if match:
                    rate = float(match.group(1))
                    print(f"Rate for {currency}: {rate}")
                    results[currency] = rate
                    found_rate = True
                    break
                else:
                    print(f"Attempt {attempt+1}: Rate not found for {currency} (Mastercard Rate context). Retrying...")

            if not found_rate:
                # Fallback: simple search if Mastercard Rate context fails (unlikely if page structure holds)
                # But risk getting ECB rate.
                print(f"Rate not found for {currency} after retries. Trying simple search...")
                pattern_simple = f"1 GBP = ([0-9.]+)\\s+{currency}"
                match_simple = re.search(pattern_simple, text_content)
                if match_simple:
                    rate = float(match_simple.group(1))
                    print(f"Rate for {currency} (Simple match): {rate}")
                    results[currency] = rate
                else:
                    print(f"Rate completely not found for {currency}.")

    except Exception as e:
        print(f"Error scraping Monzo: {e}")
        return None
    finally:
        if browser:
            await browser.close()

    return results

def update_sitemap(timestamp, filepath='sitemap.xml'):
    """Generates a sitemap.xml with the current date as lastmod."""
    date_str = timestamp.strftime("%Y-%m-%d")

    # List all your supported languages here
    # Adding trailing slash for directories is standard for folder-based URLs
    langs = ['', 'es/', 'pt/', 'he/', 'fr/', 'de/', 'zh/', 'ko/']

    url_entries = ""
    for lang in langs:
        url_entries += f"""
  <url>
    <loc>https://boliviatravelmoney.site/{lang}</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>daily</changefreq>
    <priority>{'1.0' if lang == '' else '0.8'}</priority>
  </url>"""

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_entries}
</urlset>"""

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        print(f"Successfully generated {filepath}")
    except Exception as e:
        print(f"Error generating sitemap: {e}")

def update_index_html(timestamp, filepath='index.html'):
    """Updates the index.html title, description, schema, and revised tag with the current date."""
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. Skipping HTML update.")
        return

    try:
        date_str = timestamp.strftime("%d %b %Y")
        print(f"Updating {filepath} with date: {date_str}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update Title
        # Regex to capture content inside <title>
        # We use capturing groups to keep tags
        title_pattern = r'(<title>)(.*?)(</title>)'

        def title_replacer(match):
            start_tag, inner_text, end_tag = match.groups()
            # Remove existing date suffix if present (e.g., " - 17 Jan 2026")
            # Pattern: space dash space digit(1-2) space word(3) space digit(4)
            clean_text = re.sub(r' - \d{1,2} [A-Za-z]{3} \d{4}$', '', inner_text)
            return f'{start_tag}{clean_text} - {date_str}{end_tag}'

        content = re.sub(title_pattern, title_replacer, content, count=1, flags=re.DOTALL)

        # Update Description
        # Regex to capture content attribute in meta description
        desc_pattern = r'(<meta\s+name="description"\s+content=")(.*?)(")'

        def desc_replacer(match):
            start_attr, inner_text, end_attr = match.groups()
            # Remove existing date prefix if present (e.g., "Updated 17 Jan 2026. ")
            clean_text = re.sub(r'^Updated \d{1,2} [A-Za-z]{3} \d{4}\. ', '', inner_text)
            return f'{start_attr}Updated {date_str}. {clean_text}{end_attr}'

        content = re.sub(desc_pattern, desc_replacer, content, count=1, flags=re.DOTALL)

        # Update Body Last Updated Date
        # Regex to find the span inside the last-updated div
        # Matches: <div id="last-updated"[^>]*>.*?<span>ANYTHING</span>
        body_pattern = r'(<div id="last-updated"[^>]*>.*?<span>)(.*?)(</span>)'

        def body_replacer(match):
            start_tag, inner_text, end_tag = match.groups()
            return f'{start_tag}Updated: {date_str}{end_tag}'

        content = re.sub(body_pattern, body_replacer, content, count=1, flags=re.DOTALL)

        # Update JSON-LD dateModified
        # Regex to find the SoftwareApplication schema and add/update dateModified
        # We look for "SoftwareApplication" schema which is identified by applicationCategory
        schema_pattern = r'("applicationCategory":\s*"FinanceApplication",)'

        # Remove old dateModified if exists
        content = re.sub(r'"dateModified":\s*".*?",\s*', '', content)

        def schema_replacer(match):
            # Inject the dateModified field right after the category
            return f'{match.group(1)}\n  "dateModified": "{timestamp.isoformat()}",'

        content = re.sub(schema_pattern, schema_replacer, content, count=1)

        # Update Revised Meta Tag
        revised_pattern = r'(<meta name="revised" content=")(.*?)(" />)'
        def revised_replacer(match):
             start, _, end = match.groups()
             return f'{start}{timestamp.strftime("%A, %B %d, %Y")}{end}'

        content = re.sub(revised_pattern, revised_replacer, content, count=1)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Successfully updated {filepath}")
    except Exception as e:
        print(f"Error updating HTML: {e}")

def main():
    cached_data = None
    output_file = 'data/rates.json'

    # Check cache
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                cached_data = json.load(f)
        except Exception as e:
            print(f"Error reading cache: {e}")

    # 1. Get Street Rate
    street_rate = get_street_rate()

    if street_rate is None:
        print("Street scraping failed.")
        # Fallback to cache
        if cached_data:
            print("Using cached street rate.")
            street_rate = cached_data.get('street_rate_bob')

    # 2. Get Monzo Rates
    official_rates = asyncio.run(get_monzo_rates())
    if official_rates is None:
        official_rates = {}

    # Check if we got enough data (GBP + at least one other)
    if len(official_rates) <= 1:
        print("Monzo scraping failed (insufficient data).")
        if cached_data and cached_data.get('official_rates'):
            print("Using cached official rates.")
            official_rates = cached_data.get('official_rates')
            # Assuming cached data has GBP base if valid

    # Construct data object
    now = datetime.now(timezone.utc)
    data = {
        "date": now.isoformat(),
        "timestamp": now.timestamp(),
        "street_rate_bob": street_rate,
        "official_rates": official_rates,
        "base": "GBP",
        "source": "scraped_monzo" if len(official_rates) > 1 else "failed_cached",
        "currency_pair": "USD_to_BOB_Cash_Sell" # Legacy field
    }

    # Save to file
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved data to {output_file}")

        # Update HTML files (root + languages)
        languages = ['es', 'pt', 'he', 'fr', 'de', 'zh', 'ko']
        files_to_update = ['index.html'] + [f'{lang}/index.html' for lang in languages]

        for filepath in files_to_update:
            update_index_html(now, filepath=filepath)

        # Update Sitemap
        update_sitemap(now)

    except Exception as e:
        print(f"Error saving file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
