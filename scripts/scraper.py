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

# Comprehensive headers to mimic a real browser
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

def extract_rate_from_text(text):
    """
    Tries multiple regex patterns to extract the rate.
    """
    # Strategy 1: Specific ID
    match = re.search(r'id="dolar-libre-buy">([0-9.,]+)</span>', text)
    if match:
        return float(match.group(1).replace(',', '.'))

    # Strategy 2: Schema.org JSON-LD
    # "price": 9.60, "priceCurrency": "BOB"
    match = re.search(r'"price":\s*([0-9.]+),\s*"priceCurrency":\s*"BOB"', text)
    if match:
        return float(match.group(1))

    # Strategy 3: rawData in script
    # {"t":1768602408000,"b":"9.60","s":"9.10"}
    # Look for the last entry in the list which might be close to the end of the line
    match = re.findall(r'"b":"([0-9.]+)"', text)
    if match:
        # Get the last one as it's likely the most recent
        return float(match[-1])

    # Strategy 4: Loose text search around "Dolar Blue"
    # Dolar Blue ... 9.60 Compra
    # Use a simpler check for number followed by "Compra"
    match = re.search(r'([0-9.,]+)\s+Compra', text)
    if match:
         try:
             return float(match.group(1).replace(',', '.'))
         except ValueError:
             pass

    return None

def get_street_rate_simple():
    print(f"Attempting to fetch {URL} using requests...")
    try:
        response = requests.get(URL, headers=BROWSER_HEADERS, timeout=15)
        response.raise_for_status()

        rate = extract_rate_from_text(response.text)
        if rate:
            print(f"Successfully extracted street rate via requests: {rate}")
            return rate
        else:
            print("Could not find rate in HTML via regex/strategies.")
            return None
    except Exception as e:
        print(f"Error fetching street rate via requests: {e}")
        return None

async def get_street_rate_scraper():
    print(f"Attempting to scrape {URL} with pyppeteer...")
    browser = None
    try:
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()

        # Apply headers
        await page.setExtraHTTPHeaders(BROWSER_HEADERS)

        # Stealth: Hide webdriver property and others
        await page.evaluateOnNewDocument("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'es'],
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)

        await page.goto(URL, {'waitUntil': 'domcontentloaded', 'timeout': 30000})

        # Wait for the selector to appear
        selector = '#dolar-libre-buy'
        try:
            await page.waitForSelector(selector, {'timeout': 30000}) # 30s timeout
            element = await page.querySelector(selector)
            if element:
                text = await page.evaluate('(element) => element.textContent', element)
                text = text.strip()
                if text:
                    return float(text.replace(',', '.'))
        except Exception:
            print("Timeout waiting for selector or selector failed. Trying fallback extraction...")

        # Fallback 1: Evaluate chartData
        try:
            # Check for window.chartData
            data = await page.evaluate('(() => { if(window.chartData && window.chartData.buyPrices && window.chartData.buyPrices.length > 0) return window.chartData.buyPrices[window.chartData.buyPrices.length-1].y; return null; })()')
            if data:
                print(f"Extracted rate from window.chartData: {data}")
                return float(data)
        except Exception as e:
            print(f"Error accessing chartData: {e}")

        # Fallback 2: Get full content and regex
        content = await page.content()
        rate = extract_rate_from_text(content)
        if rate:
             print(f"Extracted rate from page content via regex: {rate}")
             return rate

        print("All scraping strategies failed.")
        return None

    except Exception as e:
        print(f"Error scraping street rate: {e}")
        return None
    finally:
        if browser:
            await browser.close()

async def get_street_rate():
    # Try simple requests first
    rate = get_street_rate_simple()
    if rate is not None:
        return rate

    # Fallback to scraper
    print("Simple fetch failed. Falling back to pyppeteer scraper...")
    return await get_street_rate_scraper()

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

        # Target currencies: USD, EUR, AUD, CAD, TWD, JPY, CNY, RUB, BOB, NZD, CHF, SGD, HKD, SEK, NOK, DKK, MXN
        # We also need these to be in the final 'official_rates' map.
        target_currencies = [
            'USD', 'EUR', 'AUD', 'CAD', 'TWD', 'JPY', 'CNY', 'RUB', 'BOB',
            'NZD', 'CHF', 'SGD', 'HKD', 'SEK', 'NOK', 'DKK', 'MXN'
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

    rate = loop.run_until_complete(get_street_rate())

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
