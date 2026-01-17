import asyncio
from pyppeteer import launch
import requests
import re
import json
import sys
import os
import time
from datetime import datetime

# Target Configuration
# Using dolarbo.com as it is easily scrapable and contains the "Dolar Blue" rate.
URL = "https://dolarbo.com"

def get_street_rate():
    try:
        print(f"Attempting to scrape {URL}...")
        # Headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(URL, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return None

        text = response.text

        # Scrape logic for dolarbo.com
        # Look for <span class="main-card-rate-value" id="dolar-libre-buy">9.60</span>
        # Or generally: id="dolar-libre-buy">NUMBER<
        # We want the "Buy" rate (e.g. 9.60) as requested by user.
        match = re.search(r'id="dolar-libre-buy">(\d+[.,]\d+)<', text)

        if match:
            return float(match.group(1).replace(',', '.'))

        print("No rate pattern found in text.")
        return None

    except Exception as e:
        print(f"Error scraping street rate: {e}")
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

        # Target currencies: USD, EUR, AUD, CAD, TWD, JPY, CNY, RUB, BOB
        # We also need these to be in the final 'official_rates' map.
        target_currencies = ['USD', 'EUR', 'AUD', 'CAD', 'TWD', 'JPY', 'CNY', 'RUB', 'BOB']

        for currency in target_currencies:
            if currency not in available_currencies:
                print(f"Warning: Currency {currency} not found in Monzo dropdown.")
                continue

            print(f"Selecting {currency}...")

            # Select the option
            # We assume the class name hasn't changed. If it has, we might need a more robust selector.
            # Using the element handle directly might be safer if possible, but page.select takes a selector string.
            # We can use the class we found earlier 'Select_input__JYjsP' or try to identify it by index.
            # Or use querySelector on the select handle? No.

            # Use a more robust selector strategy.
            # We found the second select is the currency switcher.
            # We can use nth-of-type or the element handle itself.
            # Since page.select takes a selector string, let's use a robust CSS selector.
            # "select[role='listbox']" or "main select:nth-of-type(2)" or simply rely on the class if consistent,
            # but user feedback suggested checking this.

            # Let's try to find a selector that doesn't rely on the hashed class name.
            # We can use the fact that it is likely the second select element on the page.
            # (First one was Region).

            # However, Pyppeteer's page.select requires a selector string.
            # We can try to evaluate a JS function to set the value and dispatch event, but select is easier.

            # Let's verify if there is a more stable attribute.
            # In the dump we saw: Select: {'class': ('Select_input__JYjsP',), 'role': 'listbox'}
            # 'role="listbox"' seems good!

            try:
                await page.select('select[role="listbox"]', currency)
            except Exception:
                 # Fallback to class if role selector fails
                 print("Fallback to class selector...")
                 await page.select('select.Select_input__JYjsP', currency)

            # Wait for update.
            await asyncio.sleep(1.0)

            text_content = await page.evaluate('document.body.innerText')

            # We want the Mastercard Rate.
            # Format: "Mastercard Rate\n1 GBP = X CURRENCY"
            # We search specifically for the pattern involving the currency code

            # Look for "Mastercard Rate" and then the rate line.
            # But the rate line is "1 GBP = ...".
            # The issue with simple regex on whole body is duplicate "1 GBP =" for ECB rate.
            # We need to ensure it's the one under "Mastercard Rate".

            # Let's try to find the text "Mastercard Rate" and extract following text.
            # Or improved regex:
            # Mastercard Rate.*?1 GBP = ([0-9.]+)\s+{currency}
            # using DOTALL

            pattern = f"Mastercard Rate.*?1 GBP = ([0-9.]+)\\s+{currency}"
            match = re.search(pattern, text_content, re.DOTALL)

            if match:
                rate = float(match.group(1))
                print(f"Rate for {currency}: {rate}")
                results[currency] = rate
            else:
                # Fallback: simple search if Mastercard Rate context fails (unlikely if page structure holds)
                # But risk getting ECB rate.
                print(f"Rate not found for {currency} (Mastercard Rate context). Trying simple search...")
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
    # Check cache
    if os.path.exists('data/rates.json'):
        try:
            with open('data/rates.json', 'r') as f:
                cached_data = json.load(f)
        except Exception as e:
            print(f"Error reading cache: {e}")

    # Run the async scraping function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    official_rates = loop.run_until_complete(get_monzo_rates())

    rate = get_street_rate()

    if rate is None:
        print("Street scraping failed.")
    else:
        print(f"Successfully scraped street rate: {rate}")

    # Fallback to cache for street rate if failed
    if rate is None and cached_data:
        print("Using cached street rate.")
        rate = cached_data.get('street_rate_bob')

    base_currency = "GBP"

    if not official_rates:
        print("Monzo scraping failed.")
        # Fallback to cache for official rates
        if cached_data and cached_data.get('official_rates'):
            print("Using cached official rates.")
            official_rates = cached_data.get('official_rates')
            base_currency = cached_data.get('base', 'USD') # Default to USD if base is missing (legacy)
    else:
        print(f"Successfully scraped Monzo rates. Count: {len(official_rates)}")

    # Construct data object
    # We maintain the "official_rates" field but now it's Monzo data (GBP base).
    # We add "base": "GBP".

    data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": datetime.now().timestamp(),
        "street_rate_bob": rate,
        "official_rates": official_rates,
        "base": base_currency,
        "source": "scraped_monzo" if official_rates else "failed_cached",
        "currency_pair": "USD_to_BOB_Cash_Sell" # Keeps legacy field
    }

    output_file = 'data/rates.json'
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved data to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
