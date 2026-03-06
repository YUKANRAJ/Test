from __future__ import annotations

import csv
import io
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pickle_shop.db"

app = Flask(__name__)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            unit_type TEXT NOT NULL CHECK(unit_type IN ('kg', 'bottle')),
            price REAL NOT NULL CHECK(price >= 0),
            barcode TEXT
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            tax_percent REAL NOT NULL,
            subtotal REAL NOT NULL,
            tax_amount REAL NOT NULL,
            total REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit_type TEXT NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        """
    )
    conn.commit()

    count = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        cur.executemany(
            "INSERT INTO products(name, unit_type, price, barcode) VALUES(?,?,?,?)",
            [
                ("Mango Pickle", "kg", 280.0, "890001"),
                ("Lemon Pickle", "kg", 240.0, "890002"),
                ("Garlic Pickle", "bottle", 120.0, "890003"),
                ("Mixed Veg Pickle", "bottle", 140.0, "890004"),
            ],
        )
        conn.commit()
    conn.close()


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/products", methods=["GET"])
def list_products() -> Any:
    search = request.args.get("search", "").strip()
    barcode = request.args.get("barcode", "").strip()
    conn = get_db()
    cur = conn.cursor()

    if barcode:
        rows = cur.execute(
            "SELECT * FROM products WHERE barcode = ? ORDER BY name", (barcode,)
        ).fetchall()
    elif search:
        rows = cur.execute(
            "SELECT * FROM products WHERE name LIKE ? ORDER BY name", (f"%{search}%",)
        ).fetchall()
    else:
        rows = cur.execute("SELECT * FROM products ORDER BY name").fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/products", methods=["POST"])
def create_product() -> Any:
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    unit_type = data.get("unit_type", "kg").strip()
    price = float(data.get("price", 0))
    barcode = data.get("barcode", "").strip() or None

    if not name:
        return jsonify({"error": "Product name is required"}), 400
    if unit_type not in {"kg", "bottle"}:
        return jsonify({"error": "Invalid unit type"}), 400

    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO products(name, unit_type, price, barcode) VALUES(?,?,?,?)",
            (name, unit_type, price, barcode),
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Product added"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Product name must be unique"}), 400


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id: int) -> Any:
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    unit_type = data.get("unit_type", "kg").strip()
    price = float(data.get("price", 0))
    barcode = data.get("barcode", "").strip() or None

    if not name:
        return jsonify({"error": "Product name is required"}), 400

    try:
        conn = get_db()
        conn.execute(
            "UPDATE products SET name=?, unit_type=?, price=?, barcode=? WHERE id=?",
            (name, unit_type, price, barcode, product_id),
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Product updated"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Product name must be unique"}), 400


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int) -> Any:
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product deleted"})


@app.route("/api/sales", methods=["POST"])
def create_sale() -> Any:
    data = request.get_json(force=True)
    items = data.get("items", [])
    tax_percent = float(data.get("tax_percent", 0))

    if not items:
        return jsonify({"error": "At least one item is required"}), 400

    conn = get_db()
    cur = conn.cursor()

    detailed_items = []
    subtotal = 0.0
    for item in items:
        product_id = int(item["product_id"])
        qty = float(item["quantity"])
        if qty <= 0:
            continue

        product = cur.execute(
            "SELECT id, name, unit_type, price FROM products WHERE id=?", (product_id,)
        ).fetchone()
        if not product:
            continue

        line_subtotal = round(product["price"] * qty, 2)
        subtotal += line_subtotal
        detailed_items.append(
            {
                "product_id": product["id"],
                "product_name": product["name"],
                "unit_type": product["unit_type"],
                "unit_price": product["price"],
                "quantity": qty,
                "subtotal": line_subtotal,
            }
        )

    if not detailed_items:
        conn.close()
        return jsonify({"error": "No valid items in bill"}), 400

    subtotal = round(subtotal, 2)
    tax_amount = round(subtotal * tax_percent / 100.0, 2)
    total = round(subtotal + tax_amount, 2)

    cur.execute(
        "INSERT INTO sales(created_at, tax_percent, subtotal, tax_amount, total) VALUES(?,?,?,?,?)",
        (datetime.now().isoformat(timespec="seconds"), tax_percent, subtotal, tax_amount, total),
    )
    sale_id = cur.lastrowid

    for row in detailed_items:
        cur.execute(
            """
            INSERT INTO sale_items(sale_id, product_id, product_name, quantity, unit_type, unit_price, subtotal)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                sale_id,
                row["product_id"],
                row["product_name"],
                row["quantity"],
                row["unit_type"],
                row["unit_price"],
                row["subtotal"],
            ),
        )

    conn.commit()
    conn.close()
    return jsonify({"message": "Sale recorded", "sale_id": sale_id, "subtotal": subtotal, "tax_amount": tax_amount, "total": total})


@app.route("/api/sales/history", methods=["GET"])
def sales_history() -> Any:
    conn = get_db()
    rows = conn.execute(
        "SELECT id, created_at, subtotal, tax_amount, total FROM sales ORDER BY id DESC LIMIT 30"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/sales/report/daily", methods=["GET"])
def daily_report() -> Any:
    conn = get_db()
    rows = conn.execute(
        """
        SELECT substr(created_at, 1, 10) AS sale_date,
               COUNT(*) AS bills,
               ROUND(SUM(total), 2) AS total_sales
        FROM sales
        GROUP BY substr(created_at, 1, 10)
        ORDER BY sale_date DESC
        LIMIT 30
        """
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/sales/export", methods=["GET"])
def export_sales() -> Any:
    conn = get_db()
    rows = conn.execute(
        "SELECT id, created_at, subtotal, tax_amount, total FROM sales ORDER BY id DESC"
    ).fetchall()
    conn.close()

    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["Sale ID", "Date Time", "Subtotal", "Tax", "Total"])
    for row in rows:
        writer.writerow([row["id"], row["created_at"], row["subtotal"], row["tax_amount"], row["total"]])

    mem = io.BytesIO(stream.getvalue().encode("utf-8"))
    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name="pickle_sales_report.csv",
    )


init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
