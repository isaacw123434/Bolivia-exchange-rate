import requests
import json
import re
from datetime import datetime
import sys
import os
import time

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
        print(f"Error scraping: {e}")
        return None

def get_official_rates(api_key):
    if not api_key:
        print("No Exchange Rate API Key provided.")
        return None

    # New API endpoint as requested
    url = "https://api.exchangerateapi.net/v1/latest"
    params = {
        "base": "USD"
    }
    headers = {
        "apikey": api_key
    }

    try:
        print(f"Fetching official rates from {url}...")
        response = requests.get(url, params=params, headers=headers, timeout=10)

        try:
            data = response.json()
        except ValueError:
            print(f"Failed to parse JSON response. Status: {response.status_code}, Body: {response.text[:100]}...")
            return None

        if response.status_code == 200 and (data.get('success') is True or 'rates' in data):
            print("Successfully fetched official rates.")
            return data.get('rates')
        else:
            # Handle API specific errors
            error_message = data.get('message') or data.get('error', {}).get('info') or "Unknown error"
            print(f"Failed to fetch official rates. Status: {response.status_code}, Error: {error_message}")
            return None

    except Exception as e:
        print(f"Error fetching official rates: {e}")
        return None

def main():
    # Check cache
    if os.path.exists('data/rates.json'):
        try:
            with open('data/rates.json', 'r') as f:
                cached_data = json.load(f)
                timestamp = cached_data.get('timestamp')
                if timestamp:
                    # 1 day in seconds
                    if (datetime.now().timestamp() - timestamp) < (24 * 3600):
                        print("Using cached rates (less than 1 day old).")
                        return
        except Exception as e:
            print(f"Error reading cache: {e}")

    rate = get_street_rate()

    if rate is None:
        print("Scraping failed.")
    else:
        print(f"Successfully scraped rate: {rate}")

    # Fetch official rates
    api_key = os.environ.get("EXCHANGE_API_KEY")
    official_rates = get_official_rates(api_key)

    # Validate Backpacking Currencies
    required_currencies = ['EUR', 'GBP', 'CAD', 'AUD', 'TWD', 'JPY', 'CNY', 'RUB']
    if official_rates:
        missing = [cur for cur in required_currencies if cur not in official_rates]
        if missing:
            print(f"Warning: The following currencies were not found in the API response: {missing}")
        else:
            print("All backpacker currencies (EU, UK, CAD, AUS, TWD, JPY, CNY, RUB) found in API.")

    data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": datetime.now().timestamp(),
        "street_rate_bob": rate,
        "official_rates": official_rates,
        "source": "scraped" if rate is not None else "failed",
        "currency_pair": "USD_to_BOB_Cash_Sell"
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
