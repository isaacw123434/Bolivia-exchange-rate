# Bolivia Blue Dollar Calculator

This project provides a web-based calculator to compare official and "Blue Dollar" exchange rates in Bolivia. It helps travelers decide whether to use cash, credit cards, or money transfer apps.

## Project Structure

- **`js/`**: Contains the frontend JavaScript logic (`app.js`) and service worker registration (`sw_register.js`).
- **`src/`**: Contains the input CSS for Tailwind (`input.css`).
- **`static/`**: Stores static assets like images, icons, manifest files, and the generated CSS (`output.css`).
- **`data/`**: Contains `rates.json`, which stores the latest exchange rates used by the application.
- **`scripts/`**: Contains `scraper.py`, a Python script used to fetch the latest street exchange rates and official rates.
- **`index.html`**: The main entry point for the web application.
- **`sw.js`**: The Service Worker file for offline capabilities.
- **`tailwind.config.js`**: Configuration file for Tailwind CSS.
- **`requirements.txt`**: Python dependencies for the scraper script.
- **`package.json`**: Node.js dependencies and scripts.

## Setup

### Prerequisites
- Node.js and npm
- Python 3.x

### Frontend Setup

1.  **Install Dependencies**:
    ```bash
    npm install
    ```

2.  **Build CSS**:
    Generate the Tailwind CSS output.
    ```bash
    npm run build:css
    ```
    For development (watch mode), you can use:
    ```bash
    npx tailwindcss -i ./src/input.css -o ./static/output.css --watch
    ```

3.  **Serve Application**:
    The frontend is a static site. You can serve it using any static file server, for example with Python:
    ```bash
    python -m http.server
    ```

### Scraper Setup

To run the scraper, install dependencies and run the script.
```bash
pip install -r requirements.txt
python scripts/scraper.py
```

## GitHub Actions

The repository includes a GitHub Action (`.github/workflows/daily_scrape.yml`) that runs the scraper daily to update `data/rates.json`.
