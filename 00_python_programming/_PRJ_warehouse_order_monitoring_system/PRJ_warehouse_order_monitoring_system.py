"""
================================================================================
PROJECT: Warehouse & Order Monitoring System — LogiServe S.r.l.
================================================================================

Author  : Simone La Porta
Date    : 2026-04-21
Python  : 3.10+
Deps    : standard library only (csv, json, pathlib, datetime)

OVERVIEW
--------
LogiServe S.r.l. is a small B2B company distributing electrical components to
workshops and resellers across northern Italy. The existing workflow relies on a
shared Excel spreadsheet, which causes synchronisation issues among staff and
provides no audit trail for stock movements or order changes.

This project replaces that spreadsheet with a command-line application that:
  - registers incoming customer orders and checks product availability upfront
  - fulfils orders by deducting the appropriate quantities from warehouse stock
  - supports partial fulfilment when stock is insufficient for a given line
  - exposes filtered views of the product catalogue and order history
  - generates a daily summary report in both TXT and CSV formats
  - persists all state to JSON files so data survives process restarts
  - maintains a full CSV audit log of every operation, with timestamps

HOW TO RUN
----------
  python PRJ_Sistema_Monitoraggio_Ordini_Magazzino.py

No external packages are required — only the Python standard library is used.
On first run, the data/ directory is created automatically and seeded with
sample products and orders, so all features can be explored immediately without
manual setup.

DATA MODEL
----------
Two entities drive the system:

  Product   code, name, category, stock, reorder_point, unit, unit_price
  Order     order_id, date, customer, priority, status, lines[], notes

Each order line links a product code to a requested quantity and the quantity
actually fulfilled at dispatch time. Order status is derived from line-level
availability:

  new         registered, not yet dispatched (all lines available)
  partial     at least one line could not be fully covered
  on_hold     at least one line has zero stock available
  fulfilled   all lines have been fully dispatched
  cancelled   manually cancelled before fulfilment

DESIGN NOTES
------------
The codebase is structured around six classes with clear, single responsibilities:

  Logger           append-only CSV audit trail
  DataManager      JSON read/write — the only layer that touches disk
  Warehouse        in-memory product catalogue and stock mutations
  OrderManager     order lifecycle: register → fulfil → cancel
  ReportGenerator  daily summary in TXT and CSV formats
  CLI              interactive menu loop; delegates all logic to the above

JSON was chosen for persistence because the files stay human-readable in a text
editor and map directly to Python lists of dicts without requiring a schema or
migration system. If concurrency or data volume became a concern, DataManager
provides a clean abstraction boundary for swapping in SQLite with minimal
changes to the rest of the code.

Stock deduction uses min(requested, available) to guarantee quantities never go
negative, even under insufficient stock. Order status is evaluated
pessimistically: a single short line pulls the entire order to "partial" or
"on_hold", making it immediately visible to operators which orders need
attention without having to inspect individual lines.

KNOWN LIMITATIONS
-----------------
  - Single-user only: concurrent writes to the JSON files are not safe.
  - No authentication: anyone who can start the process has full access.
  - No undo for stock deductions beyond entering a manual adjustment.

================================================================================
"""

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
PRODUCTS_FILE = DATA_DIR / "products.json"
ORDERS_FILE = DATA_DIR / "orders.json"
LOG_FILE = DATA_DIR / "operations_log.csv"

VALID_PRIORITIES = ["low", "normal", "high", "urgent"]
ORDER_STATUSES = ["new", "fulfilled", "partial", "cancelled", "on_hold"]
DEFAULT_OPERATOR = "system"


# Sample data loaded on first run so the application can be tested immediately.
INITIAL_PRODUCTS: list[dict[str, Any]] = [
    {
        "code": "P001",
        "name": "Miniature circuit breaker 16A",
        "category": "Protection",
        "stock": 120,
        "reorder_point": 30,
        "unit": "pcs",
        "unit_price": 8.50
    },
    {
        "code": "P002",
        "name": "Electrical cable 2.5mm² (100m coil)",
        "category": "Wiring",
        "stock": 45,
        "reorder_point": 15,
        "unit": "coil",
        "unit_price": 42.00
    },
    {
        "code": "P003",
        "name": "Industrial socket 32A IP44",
        "category": "Connectors",
        "stock": 60,
        "reorder_point": 20,
        "unit": "pcs",
        "unit_price": 15.90
    },
    {
        "code": "P004",
        "name": "Electrical enclosure 24 modules",
        "category": "Enclosures",
        "stock": 18,
        "reorder_point": 10,
        "unit": "pcs",
        "unit_price": 35.00
    },
    {
        "code": "P005",
        "name": "Residual current device 25A 30mA",
        "category": "Protection",
        "stock": 85,
        "reorder_point": 25,
        "unit": "pcs",
        "unit_price": 22.00
    },
    {
        "code": "P006",
        "name": "Screw terminal 4mm² (box of 100)",
        "category": "Connectors",
        "stock": 32,
        "reorder_point": 10,
        "unit": "box",
        "unit_price": 18.50
    },
    {
        "code": "P007",
        "name": "PVC cable duct 40x25mm (2m bar)",
        "category": "Wiring",
        "stock": 200,
        "reorder_point": 50,
        "unit": "bar",
        "unit_price": 3.20
    },
    {
        "code": "P008",
        "name": "Transformer 230V/24V 60VA",
        "category": "Transformers",
        "stock": 12,
        "reorder_point": 8,
        "unit": "pcs",
        "unit_price": 28.00
    },
]

# Three sample orders in different states so all menu paths can be tested immediately.
INITIAL_ORDERS: list[dict[str, Any]] = [
    {
        "order_id": "ORD-2026-001",
        "date": "2026-04-18",
        "customer": "Officina Rossi & Figli",
        "priority": "normal",
        "status": "fulfilled",
        "lines": [
            {"code": "P001", "quantity_requested": 20, "quantity_fulfilled": 20},
            {"code": "P003", "quantity_requested": 10, "quantity_fulfilled": 10},
        ],
        "notes": ""
    },
    {
        "order_id": "ORD-2026-002",
        "date": "2026-04-19",
        "customer": "Elettroforniture Bianchi",
        "priority": "high",
        "status": "partial",
        "lines": [
            {"code": "P002", "quantity_requested": 20, "quantity_fulfilled": 15},
            {"code": "P005", "quantity_requested": 30, "quantity_fulfilled": 30},
        ],
        "notes": "P002 partially fulfilled — insufficient stock at time of dispatch"
    },
    {
        "order_id": "ORD-2026-003",
        "date": "2026-04-20",
        "customer": "Rivendita Verdi S.n.c.",
        "priority": "urgent",
        "status": "new",
        "lines": [
            {"code": "P004", "quantity_requested": 5, "quantity_fulfilled": 0},
            {"code": "P008", "quantity_requested": 3, "quantity_fulfilled": 0},
        ],
        "notes": ""
    },
]


# ==============================================================================
# Logger
# ==============================================================================

class Logger:
    """Appends every system operation to a CSV file for auditing purposes."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._init_file()

    def _init_file(self):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "operator", "operation", "resource", "detail"])

    def log(self, operation: str, resource: str, detail: str = "", operator: str = DEFAULT_OPERATOR):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, operator, operation, resource, detail])
        except OSError:
            # A log write failure should never crash the application.
            pass

    def get_today_log(self) -> list[dict[str, Any]]:
        """Returns all log entries recorded today."""
        today = date.today().strftime("%Y-%m-%d")
        entries: list[dict[str, Any]] = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["timestamp"].startswith(today):
                        entries.append(dict(row))
        except FileNotFoundError:
            pass
        return entries


# ==============================================================================
# DataManager
# ==============================================================================

class DataManager:
    """
    Handles all JSON persistence. Isolating I/O here means the storage backend
    can be swapped (e.g., SQLite) without touching any other class.
    """

    def __init__(self, logger: Logger):
        self.logger = logger
        DATA_DIR.mkdir(exist_ok=True)
        REPORTS_DIR.mkdir(exist_ok=True)

    def load_products(self) -> list[dict[str, Any]]:
        if not PRODUCTS_FILE.exists():
            self._save_json(PRODUCTS_FILE, INITIAL_PRODUCTS)
            self.logger.log("INIT", "products.json", f"Seeded {len(INITIAL_PRODUCTS)} products")
        return self._load_json(PRODUCTS_FILE)

    def save_products(self, products: list[dict[str, Any]]):
        self._save_json(PRODUCTS_FILE, products)
        self.logger.log("SAVE", "products.json", f"{len(products)} products written")

    def load_orders(self) -> list[dict[str, Any]]:
        if not ORDERS_FILE.exists():
            self._save_json(ORDERS_FILE, INITIAL_ORDERS)
            self.logger.log("INIT", "orders.json", f"Seeded {len(INITIAL_ORDERS)} orders")
        return self._load_json(ORDERS_FILE)

    def save_orders(self, orders: list[dict[str, Any]]):
        self._save_json(ORDERS_FILE, orders)
        self.logger.log("SAVE", "orders.json", f"{len(orders)} orders written")

    @staticmethod
    def _load_json(path: Path) -> list[dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {path}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Corrupted data file {path}: {exc}") from exc
        except PermissionError:
            raise PermissionError(f"No read permission for {path}")

    @staticmethod
    def _save_json(path: Path, data: Any):
        # ensure_ascii=False preserves non-ASCII characters (e.g., accented letters).
        # indent=2 keeps files readable in a plain text editor.
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except PermissionError:
            raise PermissionError(f"No write permission for {path}")
        except OSError as exc:
            raise OSError(f"Failed to write {path}: {exc}") from exc


# ==============================================================================
# Warehouse
# ==============================================================================

class Warehouse:
    """In-memory product catalogue. Stock mutations are persisted on demand via save()."""

    def __init__(self, data_manager: DataManager, logger: Logger):
        self.dm = data_manager
        self.logger = logger
        self.products: list[dict[str, Any]] = self.dm.load_products()

    def save(self):
        self.dm.save_products(self.products)

    def get_product(self, code: str) -> Optional[dict[str, Any]]:
        for p in self.products:
            if p["code"].upper() == code.upper():
                return p
        return None

    def get_filtered_products(
        self,
        code: str = "",
        category: str = "",
        below_reorder: bool = False
    ) -> list[dict[str, Any]]:
        """Returns products matching all provided filters; empty/False filters are ignored."""
        results = self.products

        if code:
            results = [p for p in results if code.upper() in p["code"].upper()]
        if category:
            results = [p for p in results if category.lower() in p["category"].lower()]
        if below_reorder:
            results = [p for p in results if p["stock"] <= p["reorder_point"]]

        return results

    def update_stock(self, code: str, delta: int, operator: str = DEFAULT_OPERATOR) -> bool:
        """
        Adjusts stock by delta (positive = receipt, negative = dispatch).
        A reorder alert is logged whenever stock falls to or below the reorder point.
        """
        product = self.get_product(code)
        if not product:
            return False

        previous = product["stock"]
        product["stock"] += delta

        self.logger.log(
            "STOCK_UPDATE",
            code,
            f"{previous} → {product['stock']} (delta: {delta:+d})",
            operator
        )

        if product["stock"] <= product["reorder_point"]:
            self.logger.log(
                "REORDER_ALERT",
                code,
                f"Stock {product['stock']} <= reorder point {product['reorder_point']}",
                operator
            )

        return True

    def add_product(self, product: dict[str, Any], operator: str = DEFAULT_OPERATOR):
        product["code"] = product["code"].upper()
        self.products.append(product)
        self.logger.log("NEW_PRODUCT", product["code"], product["name"], operator)

    def categories(self) -> list[str]:
        return sorted(set(p["category"] for p in self.products))

    def products_below_reorder(self) -> list[dict[str, Any]]:
        return [p for p in self.products if p["stock"] <= p["reorder_point"]]


# ==============================================================================
# OrderManager
# ==============================================================================

class OrderManager:
    """
    Manages the full order lifecycle: registration, fulfilment, and cancellation.

    Registration records the order and checks availability but does not touch stock.
    Fulfilment deducts stock line by line using min(requested, available), which
    guarantees quantities never go negative. The final order status is determined
    pessimistically: a single unmet line downgrades the entire order to "partial"
    or "on_hold".
    """

    def __init__(self, data_manager: DataManager, warehouse: Warehouse, logger: Logger):
        self.dm = data_manager
        self.wh = warehouse
        self.logger = logger
        self.orders: list[dict[str, Any]] = self.dm.load_orders()

    def save(self):
        self.dm.save_orders(self.orders)

    def _generate_id(self) -> str:
        """Generates the next order ID in the format ORD-YEAR-NNN."""
        year = datetime.now().year
        year_orders = [o["order_id"] for o in self.orders if str(year) in o["order_id"]]
        if not year_orders:
            return f"ORD-{year}-001"
        numbers = [int(oid.split("-")[-1]) for oid in year_orders]
        return f"ORD-{year}-{max(numbers) + 1:03d}"

    def register_order(
        self,
        customer: str,
        lines: list[dict[str, Any]],
        priority: str = "normal",
        operator: str = DEFAULT_OPERATOR
    ) -> dict[str, Any]:
        """
        Creates a new order and pre-checks availability for each line.
        Stock is not modified at registration time.
        """
        order_id = self._generate_id()
        today = date.today().strftime("%Y-%m-%d")
        processed_lines: list[dict[str, Any]] = []
        status = "new"

        for line in lines:
            code = line["code"].upper()
            qty_requested = line["quantity"]
            product = self.wh.get_product(code)

            if not product:
                processed_lines.append({
                    "code": code,
                    "quantity_requested": qty_requested,
                    "quantity_fulfilled": 0,
                    "availability": "product_not_found"
                })
                status = "on_hold"
                continue

            stock = product["stock"]
            if stock >= qty_requested:
                availability = "available"
            elif stock > 0:
                availability = "partial"
                if status == "new":
                    status = "partial"
            else:
                availability = "unavailable"
                status = "on_hold"

            processed_lines.append({
                "code": code,
                "quantity_requested": qty_requested,
                "quantity_fulfilled": 0,
                "availability": availability
            })

        new_order: dict[str, Any] = {
            "order_id": order_id,
            "date": today,
            "customer": customer,
            "priority": priority,
            "status": status,
            "lines": processed_lines,
            "notes": ""
        }
        self.orders.append(new_order)
        self.logger.log(
            "NEW_ORDER",
            order_id,
            f"Customer: {customer} | Priority: {priority} | Status: {status}",
            operator
        )
        return new_order

    def fulfill_order(self, order_id: str, operator: str = DEFAULT_OPERATOR) -> tuple[bool, str]:
        """
        Dispatches an order. Each line is fulfilled up to available stock.
        The order reaches "fulfilled" status only when every line is fully covered.
        """
        order = self.get_order(order_id)
        if not order:
            return False, f"Order {order_id} not found."
        if order["status"] == "fulfilled":
            return False, f"Order {order_id} has already been fulfilled."
        if order["status"] == "cancelled":
            return False, f"Order {order_id} is cancelled and cannot be fulfilled."

        fully_fulfilled = True
        messages: list[str] = []

        for line in order["lines"]:
            code = line["code"]
            remaining = line["quantity_requested"] - line["quantity_fulfilled"]

            if remaining <= 0:
                continue

            product = self.wh.get_product(code)
            if not product:
                messages.append(f"  {code}: product not found in warehouse")
                fully_fulfilled = False
                continue

            to_dispatch = min(remaining, product["stock"])

            if to_dispatch > 0:
                self.wh.update_stock(code, -to_dispatch, operator)
                line["quantity_fulfilled"] += to_dispatch
                line["availability"] = "available" if to_dispatch == remaining else "partial"

            if line["quantity_fulfilled"] < line["quantity_requested"]:
                fully_fulfilled = False
                short = line["quantity_requested"] - line["quantity_fulfilled"]
                messages.append(
                    f"  {code}: dispatched {line['quantity_fulfilled']}/{line['quantity_requested']} — {short} short"
                )
            else:
                messages.append(
                    f"  {code}: dispatched {line['quantity_fulfilled']}/{line['quantity_requested']} ✓"
                )

        order["status"] = "fulfilled" if fully_fulfilled else "partial"
        self.logger.log(
            "ORDER_FULFILL",
            order_id,
            f"Final status: {order['status']} | Operator: {operator}",
            operator
        )
        summary = f"Order {order_id} — status: {order['status'].upper()}\n" + "\n".join(messages)
        return True, summary

    def cancel_order(self, order_id: str, operator: str = DEFAULT_OPERATOR) -> tuple[bool, str]:
        """Cancels an order. Already-fulfilled orders cannot be cancelled."""
        order = self.get_order(order_id)
        if not order:
            return False, f"Order {order_id} not found."
        if order["status"] == "fulfilled":
            return False, "Fulfilled orders cannot be cancelled."
        order["status"] = "cancelled"
        self.logger.log("ORDER_CANCEL", order_id, f"Customer: {order['customer']}", operator)
        return True, f"Order {order_id} cancelled."

    def get_order(self, order_id: str) -> Optional[dict[str, Any]]:
        for o in self.orders:
            if o["order_id"] == order_id:
                return o
        return None

    def get_filtered_orders(
        self,
        status: str = "",
        customer: str = "",
        date_from: str = "",
        date_to: str = ""
    ) -> list[dict[str, Any]]:
        """
        Filters orders by any combination of status, customer substring, and date range.
        Date strings are compared lexicographically, which is correct for ISO 8601 format.
        """
        results = self.orders

        if status:
            results = [o for o in results if o["status"] == status]
        if customer:
            results = [o for o in results if customer.lower() in o["customer"].lower()]
        if date_from:
            results = [o for o in results if o["date"] >= date_from]
        if date_to:
            results = [o for o in results if o["date"] <= date_to]

        return results

    def orders_today(self) -> list[dict[str, Any]]:
        today = date.today().strftime("%Y-%m-%d")
        return [o for o in self.orders if o["date"] == today]


# ==============================================================================
# ReportGenerator
# ==============================================================================

class ReportGenerator:
    """Generates a daily summary report in plain-text and CSV formats."""

    def __init__(self, warehouse: Warehouse, order_manager: OrderManager, logger: Logger):
        self.wh = warehouse
        self.om = order_manager
        self.logger = logger

    def generate_daily_report(self, report_date: str = "") -> tuple[str, str]:
        """
        Generates the report for report_date (defaults to today).
        Returns the report text and the path to the saved CSV file.
        """
        if not report_date:
            report_date = date.today().strftime("%Y-%m-%d")

        day_orders = [o for o in self.om.orders if o["date"] == report_date]
        fulfilled  = [o for o in day_orders if o["status"] == "fulfilled"]
        partial    = [o for o in day_orders if o["status"] == "partial"]
        pending    = [o for o in day_orders if o["status"] in ("new", "on_hold")]
        cancelled  = [o for o in day_orders if o["status"] == "cancelled"]

        # Aggregate quantities dispatched today to find the top-moving products.
        dispatched: dict[str, int] = {}
        for order in day_orders:
            for line in order["lines"]:
                code = line["code"]
                dispatched[code] = dispatched.get(code, 0) + line.get("quantity_fulfilled", 0)
        top_products = sorted(dispatched.items(), key=lambda x: x[1], reverse=True)[:5]

        low_stock = self.wh.products_below_reorder()

        sep  = "=" * 60
        hdiv = "-" * 60

        rows = [
            sep,
            f"  DAILY REPORT — LogiServe S.r.l.",
            f"  Date: {report_date}",
            f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            sep, "",
            "ORDER SUMMARY", hdiv,
            f"  Orders received today : {len(day_orders)}",
            f"  Fulfilled             : {len(fulfilled)}",
            f"  Partial               : {len(partial)}",
            f"  Pending               : {len(pending)}",
            f"  Cancelled             : {len(cancelled)}", "",
        ]

        if top_products:
            rows += ["TOP PRODUCTS (TODAY)", hdiv]
            for code, qty in top_products:
                product = self.wh.get_product(code)
                name = product["name"] if product else code
                rows.append(f"  {code} — {name}: {qty} units dispatched")
            rows.append("")

        rows += [
            "STOCK STATUS", hdiv,
            f"  {'Code':<8} {'Name':<35} {'Stock':>7} {'Reorder':>8} {'Unit':<6} {'Status':<14}",
            f"  {'-'*8} {'-'*35} {'-'*7} {'-'*8} {'-'*6} {'-'*14}",
        ]
        for p in sorted(self.wh.products, key=lambda x: x["code"]):
            if p["stock"] == 0:
                stock_status = "✗ OUT OF STOCK"
            elif p["stock"] <= p["reorder_point"]:
                stock_status = "⚠ REORDER"
            else:
                stock_status = "OK"
            rows.append(
                f"  {p['code']:<8} {p['name'][:35]:<35} {p['stock']:>7} "
                f"{p['reorder_point']:>8} {p['unit']:<6} {stock_status:<14}"
            )
        rows.append("")

        if low_stock:
            rows += ["REORDER ALERTS", hdiv]
            for p in low_stock:
                rows.append(
                    f"  {p['code']} — {p['name']}: stock {p['stock']} (threshold: {p['reorder_point']})"
                )
            rows.append("")

        if pending:
            rows += ["PENDING ORDERS", hdiv]
            for o in pending:
                rows.append(f"  {o['order_id']} | {o['customer']} | Priority: {o['priority']}")
            rows.append("")

        rows.append(sep)
        text = "\n".join(rows)

        txt_path = REPORTS_DIR / f"report_{report_date}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Three-column layout (Section, Field, Value) makes the CSV easy to filter in Excel.
        csv_path = REPORTS_DIR / f"report_{report_date}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Section", "Field", "Value"])
            writer.writerow(["Summary", "Report date", report_date])
            writer.writerow(["Summary", "Orders received", len(day_orders)])
            writer.writerow(["Summary", "Fulfilled", len(fulfilled)])
            writer.writerow(["Summary", "Partial", len(partial)])
            writer.writerow(["Summary", "Pending", len(pending)])
            writer.writerow(["Summary", "Cancelled", len(cancelled)])
            for code, qty in top_products:
                writer.writerow(["Top product", code, qty])
            for p in self.wh.products:
                writer.writerow(["Stock", p["code"], p["stock"]])
            for p in low_stock:
                writer.writerow(["Reorder alert", p["code"], p["stock"]])

        self.logger.log("REPORT", f"report_{report_date}", f"Saved to {txt_path} and {csv_path}")
        return text, str(csv_path)


# ==============================================================================
# CLI
# ==============================================================================

class CLI:
    """Interactive menu loop. All business logic is delegated to the classes above."""

    def __init__(self):
        # Logger must be instantiated first because every other component uses it during init.
        logger = Logger(LOG_FILE)
        dm = DataManager(logger)
        self.wh = Warehouse(dm, logger)
        self.om = OrderManager(dm, self.wh, logger)
        self.rg = ReportGenerator(self.wh, self.om, logger)
        self.logger = logger
        self.operator = "operator"

    @staticmethod
    def _print_header(title: str):
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")

    @staticmethod
    def _input(prompt: str) -> str:
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")
            return ""

    @staticmethod
    def _input_int(prompt: str, minimum: int = 1) -> Optional[int]:
        """Prompts for an integer. Returns None if the user submits an empty string."""
        while True:
            val = CLI._input(prompt)
            if val == "":
                return None
            try:
                n = int(val)
                if n < minimum:
                    print(f"  Please enter a value >= {minimum}.")
                    continue
                return n
            except ValueError:
                print("  Invalid value — please enter an integer.")

    @staticmethod
    def _confirm(question: str) -> bool:
        """Asks a yes/no question. Defaults to No."""
        answer = CLI._input(f"{question} [y/N]: ").lower()
        return answer in ("y", "yes")

    def run(self):
        print("\n  Welcome to LogiServe — Warehouse & Order Monitoring System")
        print(f"  Current operator: {self.operator}")
        self._warn_low_stock_startup()
        while True:
            self._print_header("MAIN MENU")
            print("  1. Orders")
            print("  2. Warehouse")
            print("  3. Reports & Log")
            print("  4. Settings")
            print("  0. Save & Exit")
            choice = self._input("\nChoice: ")
            if choice == "1":
                self._orders_menu()
            elif choice == "2":
                self._warehouse_menu()
            elif choice == "3":
                self._report_menu()
            elif choice == "4":
                self._settings_menu()
            elif choice == "0":
                self._quit()
                break
            else:
                print("  Invalid choice.")

    def _warn_low_stock_startup(self):
        low = self.wh.products_below_reorder()
        if low:
            print(f"\n  ⚠  WARNING: {len(low)} product(s) below reorder point:")
            for p in low:
                print(f"     {p['code']} — {p['name']}: stock {p['stock']} (threshold {p['reorder_point']})")

    # --- Orders ---

    def _orders_menu(self):
        while True:
            self._print_header("ORDERS")
            print("  1. Register new order")
            print("  2. Fulfil order")
            print("  3. Cancel order")
            print("  4. View orders")
            print("  5. Order detail")
            print("  0. Back")
            choice = self._input("\nChoice: ")
            if choice == "1":
                self._register_order()
            elif choice == "2":
                self._fulfill_order()
            elif choice == "3":
                self._cancel_order()
            elif choice == "4":
                self._view_orders()
            elif choice == "5":
                self._order_detail()
            elif choice == "0":
                break
            else:
                print("  Invalid choice.")

    def _register_order(self):
        self._print_header("REGISTER NEW ORDER")

        customer = self._input("Customer: ")
        if not customer:
            print("  Customer name is required.")
            return

        print(f"  Available priorities: {', '.join(VALID_PRIORITIES)}")
        priority = self._input("Priority [normal]: ").lower() or "normal"
        if priority not in VALID_PRIORITIES:
            print("  Unrecognised priority — defaulting to 'normal'.")
            priority = "normal"

        lines: list[dict[str, Any]] = []
        print("\n  Enter order lines (leave code blank to finish):")
        while True:
            code = self._input("  Product code: ").upper()
            if not code:
                break

            product = self.wh.get_product(code)
            if not product:
                print(f"  ⚠  Product {code} not found in catalogue.")
                if not self._confirm("  Add to order anyway?"):
                    continue
            else:
                print(f"  → {product['name']} | Current stock: {product['stock']} {product['unit']}")

            quantity = self._input_int("  Quantity: ", minimum=1)
            if quantity is None:
                continue
            lines.append({"code": code, "quantity": quantity})

        if not lines:
            print("  No products entered — order not created.")
            return

        order = self.om.register_order(customer, lines, priority, self.operator)
        print(f"\n  Order registered: {order['order_id']}")
        print(f"  Status: {order['status'].upper()}")
        for ln in order["lines"]:
            print(f"  {ln['code']}: requested {ln['quantity_requested']} — availability: {ln.get('availability', '?')}")

        self.om.save()

    def _fulfill_order(self):
        self._print_header("FULFIL ORDER")
        self._print_orders_brief(status_filter=["new", "partial", "on_hold"])

        order_id = self._input("\nOrder ID to fulfil: ").upper()
        if not order_id:
            return
        if not self._confirm(f"Confirm fulfilment of {order_id}?"):
            return

        ok, msg = self.om.fulfill_order(order_id, self.operator)
        print(f"\n{msg}")

        if ok:
            self.om.save()
            self.wh.save()
            self._warn_low_stock_post_fulfil()

    def _cancel_order(self):
        self._print_header("CANCEL ORDER")
        self._print_orders_brief(status_filter=["new", "partial", "on_hold"])

        order_id = self._input("\nOrder ID to cancel: ").upper()
        if not order_id:
            return
        if not self._confirm(f"Cancel order {order_id}?"):
            return

        ok, msg = self.om.cancel_order(order_id, self.operator)
        print(f"\n  {msg}")
        if ok:
            self.om.save()

    def _view_orders(self):
        self._print_header("VIEW ORDERS")
        print("  Optional filters (press Enter to skip):")
        status    = self._input(f"  Status ({'/'.join(ORDER_STATUSES)}): ").lower()
        customer  = self._input("  Customer (partial match): ")
        date_from = self._input("  From date (YYYY-MM-DD): ")
        date_to   = self._input("  To date   (YYYY-MM-DD): ")

        orders = self.om.get_filtered_orders(status, customer, date_from, date_to)
        if not orders:
            print("  No orders found for the given filters.")
            return

        print(f"\n  {'Order ID':<18} {'Date':<12} {'Customer':<28} {'Priority':<10} {'Status':<12}")
        print(f"  {'-'*18} {'-'*12} {'-'*28} {'-'*10} {'-'*12}")
        for o in orders:
            print(
                f"  {o['order_id']:<18} {o['date']:<12} {o['customer'][:28]:<28} "
                f"{o['priority']:<10} {o['status']:<12}"
            )
        print(f"\n  Found: {len(orders)} orders")

    def _order_detail(self):
        self._print_header("ORDER DETAIL")
        order_id = self._input("Order ID: ").upper()
        if not order_id:
            return
        order = self.om.get_order(order_id)
        if not order:
            print(f"  Order {order_id} not found.")
            return

        print(f"\n  Order ID  : {order['order_id']}")
        print(f"  Date      : {order['date']}")
        print(f"  Customer  : {order['customer']}")
        print(f"  Priority  : {order['priority']}")
        print(f"  Status    : {order['status'].upper()}")
        if order["notes"]:
            print(f"  Notes     : {order['notes']}")

        print(f"\n  {'Code':<8} {'Requested':>10} {'Fulfilled':>10} {'Availability':<18}")
        print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*18}")
        for ln in order["lines"]:
            product = self.wh.get_product(ln["code"])
            name = f"({product['name'][:20]})" if product else ""
            print(
                f"  {ln['code']:<8} {ln['quantity_requested']:>10} {ln['quantity_fulfilled']:>10} "
                f"{ln.get('availability', '?'):<18} {name}"
            )

    def _print_orders_brief(self, status_filter: Optional[list[str]] = None):
        """Prints a compact order list used as reference before asking for an order ID."""
        orders = self.om.orders
        if status_filter:
            orders = [o for o in orders if o["status"] in status_filter]
        if not orders:
            print("  No orders available.")
            return
        print(f"\n  {'Order ID':<18} {'Customer':<28} {'Status':<12} {'Priority'}")
        print(f"  {'-'*18} {'-'*28} {'-'*12} {'-'*10}")
        for o in orders[-15:]:
            print(f"  {o['order_id']:<18} {o['customer'][:28]:<28} {o['status']:<12} {o['priority']}")

    # --- Warehouse ---

    def _warehouse_menu(self):
        while True:
            self._print_header("WAREHOUSE")
            print("  1. View products")
            print("  2. Products below reorder point")
            print("  3. Manual stock adjustment")
            print("  4. Add new product")
            print("  0. Back")
            choice = self._input("\nChoice: ")
            if choice == "1":
                self._view_products()
            elif choice == "2":
                self._reorder_products()
            elif choice == "3":
                self._update_stock_manual()
            elif choice == "4":
                self._add_product()
            elif choice == "0":
                break
            else:
                print("  Invalid choice.")

    def _view_products(self):
        self._print_header("PRODUCT CATALOGUE")
        print("  Optional filters (press Enter to skip):")
        code = self._input("  Code: ")
        print(f"  Available categories: {', '.join(self.wh.categories())}")
        category = self._input("  Category: ")
        below_str = self._input("  Only products below reorder point? [y/N]: ").lower()
        below_reorder = below_str in ("y", "yes")

        products = self.wh.get_filtered_products(code, category, below_reorder)
        if not products:
            print("  No products found.")
            return

        print(
            f"\n  {'Code':<8} {'Name':<35} {'Stock':>7} {'Reorder':>8} "
            f"{'Unit':<6} {'Price':>8} {'Status'}"
        )
        print(f"  {'-'*8} {'-'*35} {'-'*7} {'-'*8} {'-'*6} {'-'*8} {'-'*12}")
        for p in sorted(products, key=lambda x: x["code"]):
            if p["stock"] == 0:
                status = "OUT OF STOCK"
            elif p["stock"] <= p["reorder_point"]:
                status = "REORDER"
            else:
                status = "OK"
            print(
                f"  {p['code']:<8} {p['name'][:35]:<35} {p['stock']:>7} "
                f"{p['reorder_point']:>8} {p['unit']:<6} "
                f"{p['unit_price']:>7.2f}€ {status}"
            )
        print(f"\n  Total: {len(products)} products")

    def _reorder_products(self):
        self._print_header("PRODUCTS BELOW REORDER POINT")
        products = self.wh.products_below_reorder()
        if not products:
            print("  All products are above their reorder point.")
            return
        for p in products:
            print(
                f"  {p['code']:<8} {p['name']:<40} "
                f"Stock: {p['stock']:>6} / Reorder: {p['reorder_point']}"
            )

    def _update_stock_manual(self):
        """Registers a manual stock receipt (+) or adjustment (-)."""
        self._print_header("MANUAL STOCK ADJUSTMENT")
        code = self._input("Product code: ").upper()
        if not code:
            return

        product = self.wh.get_product(code)
        if not product:
            print(f"  Product {code} not found.")
            return

        print(f"  {product['name']} — Current stock: {product['stock']} {product['unit']}")
        print("  Enter the adjustment (e.g. +50 for a receipt, -10 for a write-off):")
        delta_str = self._input("  Adjustment: ")
        if not delta_str:
            return

        try:
            delta = int(delta_str)
        except ValueError:
            print("  Invalid value — please enter an integer.")
            return

        new_stock = product["stock"] + delta
        if new_stock < 0:
            print(f"  Warning: this would bring stock to {new_stock} (negative).")
            if not self._confirm("Continue anyway?"):
                return

        self.wh.update_stock(code, delta, self.operator)
        self.wh.save()
        # product["stock"] reflects the updated value because update_stock mutates the dict in place.
        print(f"  Stock updated: {product['stock']} {product['unit']}")

    def _add_product(self):
        self._print_header("ADD NEW PRODUCT")

        code = self._input("Code (e.g. P009): ").upper()
        if not code:
            return
        if self.wh.get_product(code):
            print(f"  A product with code {code} already exists.")
            return

        name = self._input("Product name: ")
        if not name:
            return

        print(f"  Existing categories: {', '.join(self.wh.categories())}")
        category      = self._input("Category: ")
        stock         = self._input_int("Initial stock: ", minimum=0) or 0
        reorder_point = self._input_int("Reorder point: ", minimum=0) or 0
        unit          = self._input("Unit of measure (e.g. pcs, m, kg): ") or "pcs"

        # Both dot and comma are accepted as decimal separators for convenience.
        price_str = self._input("Unit price (€): ")
        try:
            unit_price = float(price_str.replace(",", "."))
        except (ValueError, AttributeError):
            unit_price = 0.0

        product: dict[str, Any] = {
            "code": code,
            "name": name,
            "category": category,
            "stock": stock,
            "reorder_point": reorder_point,
            "unit": unit,
            "unit_price": unit_price
        }
        self.wh.add_product(product, self.operator)
        self.wh.save()
        print(f"  Product {code} added to catalogue.")

    def _warn_low_stock_post_fulfil(self):
        low = self.wh.products_below_reorder()
        if low:
            print(f"\n  ⚠  Products that fell below reorder point after fulfilment:")
            for p in low:
                print(f"     {p['code']} — {p['name']}: stock {p['stock']} (threshold {p['reorder_point']})")

    # --- Reports & Log ---

    def _report_menu(self):
        while True:
            self._print_header("REPORTS & LOG")
            print("  1. Generate today's report")
            print("  2. Generate report for a specific date")
            print("  3. View today's operation log")
            print("  0. Back")
            choice = self._input("\nChoice: ")
            if choice == "1":
                self._generate_report()
            elif choice == "2":
                date_input = self._input("Date (YYYY-MM-DD): ")
                if date_input:
                    self._generate_report(date_input)
            elif choice == "3":
                self._view_log()
            elif choice == "0":
                break
            else:
                print("  Invalid choice.")

    def _generate_report(self, report_date: str = ""):
        print("\n  Generating report...")
        text, csv_path = self.rg.generate_daily_report(report_date)
        print(text)
        print(f"\n  CSV saved to: {csv_path}")
        print(f"  TXT saved to: {csv_path.replace('.csv', '.txt')}")

    def _view_log(self):
        self._print_header("OPERATION LOG — TODAY")
        entries = self.logger.get_today_log()
        if not entries:
            print("  No operations logged today.")
            return
        print(f"\n  {'Timestamp':<20} {'Operation':<25} {'Resource':<15} {'Detail'}")
        print(f"  {'-'*20} {'-'*25} {'-'*15} {'-'*30}")
        for e in entries:
            print(
                f"  {e['timestamp']:<20} {e['operation']:<25} "
                f"{e['resource']:<15} {e['detail'][:40]}"
            )

    # --- Settings ---

    def _settings_menu(self):
        self._print_header("SETTINGS")
        print(f"  Current operator: {self.operator}")
        new_name = self._input("New operator name (Enter to keep current): ")
        if new_name:
            self.operator = new_name
            print(f"  Operator set to: {self.operator}")

    def _quit(self):
        print("\n  Saving data...")
        self.wh.save()
        self.om.save()
        print("  Data saved. Goodbye!\n")


if __name__ == "__main__":
    try:
        cli = CLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!")
        sys.exit(0)
