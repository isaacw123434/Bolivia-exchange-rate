import requests
import json
import sys
import os
from datetime import datetime, timezone, timedelta
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
    data = {
        "date": datetime.now(timezone.utc).isoformat(),
        "timestamp": datetime.now(timezone.utc).timestamp(),
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
    except Exception as e:
        print(f"Error saving file: {e}")
        sys.exit(1)

    # 3. Update index.html with static date for SEO
    try:
        update_index_html(datetime.now(timezone.utc))
    except Exception as e:
        print(f"Error updating index.html: {e}")

def update_index_html(date_obj):
    """
    Updates index.html with the current date in the meta description and the displayed div.
    Format: DD/MM/YYYY, HH:MM:SS GMT-5
    """
    html_path = 'index.html'
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return

    print(f"Updating {html_path} with current date...")

    # Calculate GMT-5 time
    # UTC is date_obj. We want to display GMT-5.
    # We can subtract 5 hours.
    gmt_minus_5 = date_obj.replace(tzinfo=timezone.utc).astimezone(timezone.utc) - timedelta(hours=5)

    # Format: 17/01/2026, 7:02:33 GMT-5
    # Note: 7:02:33 (no AM/PM in user request example? "7:02:33")
    # Actually user example: "17/01/2026, 7:02:33 GMT-5"
    formatted_date = gmt_minus_5.strftime("%d/%m/%Y, %-H:%M:%S GMT-5")
    # %-H is platform specific (Linux). If on Windows use %#H.
    # Or just %H for 0-padded (which 7 is not in example? "7:02:33" usually implies no padding or 07).
    # User wrote "7:02:33".
    # If it is PM, 7 would be 19. If AM, 7 is 7.
    # Let's assume %H (24 hour) or %I (12 hour). "7" suggests 12 hour or just morning.
    # I'll use %H:%M:%S to be safe standard. Or %-I if 12 hour.
    # Let's stick to %H:%M:%S for 24h which is unambiguous, or matches user input.
    # The user example: "7:02:33".

    # Let's just use strftime default %H (07). If user wants "7", I can strip the leading zero.
    formatted_date = gmt_minus_5.strftime("%d/%m/%Y, %H:%M:%S GMT-5")

    # Strip leading zero from hour if strictly following "7:02:33" appearance for single digits
    if formatted_date.split(', ')[1].startswith('0'):
         formatted_date = formatted_date.replace(', 0', ', ', 1)

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Meta Description
    # Regex to find content="..."
    # <meta name="description" content="...">

    def replace_meta(match):
        original_content = match.group(1)
        # Remove existing "Updated: ... . " if present to avoid duplication
        clean_content = re.sub(r'^Updated: .*?\. ', '', original_content)
        return f'<meta name="description" content="Updated: {formatted_date}. {clean_content}">'

    new_content = re.sub(r'<meta name="description" content="(.*?)">', replace_meta, content)

    # 2. Update #last-updated div
    # <div id="last-updated" ...>\n        <svg ...>...</svg>\n        <span>Loading rates...</span>\n    </div>
    # We want to replace the inner content or just the span.
    # The existing content has a span with "Loading rates...".

    # Helper to find the div content
    # We look for id="last-updated" then capture until </div>
    # This is risky with regex if nested divs, but this div seems simple.

    # Actually, let's just replace the "<span>Loading rates...</span>" or "<span>Updated: ...</span>"
    # inside that specific block if we can locate it.

    # But the id is unique.
    # Let's match the whole div block.
    # <div id="last-updated"[^>]*>.*?</div>

    # Pattern to match the div opening, content, and closing.
    # Using DOTALL.
    pattern_div = r'(<div id="last-updated"[^>]*>)(.*?)(</div>)'

    def replace_div_content(match):
        div_open = match.group(1)
        # We want to keep the SVG if possible.
        # The SVG is inside group 2.
        inner = match.group(2)

        # Check if SVG exists in inner, preserve it.
        svg_match = re.search(r'<svg.*?</svg>', inner, re.DOTALL)
        svg_html = svg_match.group(0) if svg_match else ''

        # New inner content
        # Note: the user might want the specific "Current Blue Dollar..." text here? No, that's the H2.
        # Just the date.
        new_inner = f'\n        {svg_html}\n        <span>Updated: {formatted_date}</span>\n    '

        return f'{div_open}{new_inner}</div>'

    new_content = re.sub(pattern_div, replace_div_content, new_content, flags=re.DOTALL)

    if new_content != content:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {html_path} successfully.")
    else:
        print("No changes made to index.html (pattern match failed?).")

if __name__ == "__main__":
    main()
