import requests
from bs4 import BeautifulSoup
import json
import sys
import os
from datetime import datetime
import time

# Target Configuration
DOLARBO_URL = "https://dolarbo.com"
MONZO_BASE_URL = "https://monzo.com/currency-converter"

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

def get_street_rate():
    """
    Scrapes the street rate (dolar blue) from dolarbo.com using requests and BeautifulSoup.
    """
    print(f"Fetching street rate from {DOLARBO_URL}...")
    try:
        response = requests.get(DOLARBO_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        buy_rate_element = soup.find(id="dolar-libre-buy")

        if buy_rate_element:
            text = buy_rate_element.text.strip()
            print(f"Found street rate: {text}")
            return float(text.replace(',', '.'))
        else:
            print("Could not find the buy rate element on dolarbo.com.")
            return None

    except Exception as e:
        print(f"Error fetching street rate: {e}")
        return None

def get_monzo_rates():
    """
    Scrapes official rates from Monzo using requests and BeautifulSoup (via __NEXT_DATA__).
    Target currencies: USD, EUR, AUD, CAD, TWD, JPY, CNY, RUB, BOB, NZD, CHF, SGD, HKD, SEK, NOK, DKK, MXN.
    Base currency is GBP.
    """
    print("Fetching Monzo rates...")
    target_currencies = [
        'USD', 'EUR', 'AUD', 'CAD', 'TWD', 'JPY', 'CNY', 'RUB', 'BOB',
        'NZD', 'CHF', 'SGD', 'HKD', 'SEK', 'NOK', 'DKK', 'MXN'
    ]

    results = {}
    # Base is GBP
    results['GBP'] = 1.0

    with requests.Session() as session:
        session.headers.update(HEADERS)

        for currency in target_currencies:
            url = f"{MONZO_BASE_URL}/gbp-to-{currency.lower()}"
            print(f"Fetching {currency} rate from {url}...")

            try:
                response = session.get(url, timeout=10)
                if response.status_code == 404:
                    print(f"Page not found for {currency}. Skipping.")
                    continue
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                next_data = soup.find('script', id='__NEXT_DATA__', type='application/json')

                if next_data:
                    data = json.loads(next_data.string)
                    # Expected path: props.pageProps.rate
                    try:
                        rate_str = data['props']['pageProps'].get('rate')
                        if rate_str:
                            rate = float(rate_str)
                            print(f"Rate for {currency}: {rate}")
                            results[currency] = rate
                        else:
                            print(f"Rate is None or empty for {currency}.")
                    except KeyError:
                        print(f"Could not find rate in JSON for {currency}.")
                else:
                    print(f"Could not find __NEXT_DATA__ for {currency}.")

            except Exception as e:
                print(f"Error fetching rate for {currency}: {e}")

            # Be nice to the server
            time.sleep(0.5)

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
    official_rates = get_monzo_rates()

    # Check if we got enough data (GBP + at least one other)
    if len(official_rates) <= 1:
        print("Monzo scraping failed (insufficient data).")
        if cached_data and cached_data.get('official_rates'):
            print("Using cached official rates.")
            official_rates = cached_data.get('official_rates')
            # Assuming cached data has GBP base if valid

    # Construct data object
    data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": datetime.now().timestamp(),
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

if __name__ == "__main__":
    main()
