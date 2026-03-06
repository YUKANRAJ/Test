# Pickle Shop Billing App

Lightweight offline-friendly billing app for pickle shops using Flask + SQLite.

## Features
- Add/Edit/Delete pickle products (kg or bottle pricing)
- Quick search and optional barcode-based lookup
- Create bills with automatic subtotal, GST, and final total
- Sales history and daily sales summary
- Export sales to CSV (open in Excel)
- Print bill or save as PDF using browser Print dialog

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open: `http://localhost:5000`

## Notes
- Data is saved in `pickle_shop.db`.
- Works offline once dependencies are installed.
