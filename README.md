# Bolivia Blue Dollar Calculator & Exchange Rate

This project provides a web-based calculator to compare official and "Blue Dollar" exchange rates in Bolivia. It helps travelers decide whether to use cash, credit cards, or money transfer apps.

## Project Structure

- **`js/`**: Contains the frontend JavaScript logic (`app.js`), service worker registration (`sw_register.js`), and Tailwind configuration (`tailwind_config.js`).
- **`static/`**: Stores static assets like images, icons, and manifest files.
- **`data/`**: Contains `rates.json`, which stores the latest exchange rates used by the application.
- **`scripts/`**: Contains `scraper.py`, a Python script used to fetch the latest street exchange rates and official rates.
- **`index.html`**: The main entry point for the web application.
- **`sw.js`**: The Service Worker file for offline capabilities.
- **`requirements.txt`**: Python dependencies for the scraper script.

## Setup

1.  **Frontend**: The frontend is a static site. You can serve it using any static file server.
    ```bash
    python -m http.server
    ```
2.  **Scraper**: To run the scraper, install dependencies and run the script.
    ```bash
    pip install -r requirements.txt
    python scripts/scraper.py
    ```

## GitHub Actions

The repository includes a GitHub Action (`.github/workflows/daily_scrape.yml`) that runs the scraper daily to update `data/rates.json`.
