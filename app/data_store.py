import csv
import re
import unicodedata
from pathlib import Path

from .settings import DATA_DIR


def _read_csv(prefix: str) -> list[dict[str, str]]:
    matches = sorted(DATA_DIR.glob(f"desafio_tecnico_ai_eng - {prefix}.csv"))
    if not matches:
        raise FileNotFoundError(f"CSV não encontrado: {prefix}")
    with matches[0].open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _text(value: str) -> str:
    # Algumas células dos arquivos fornecidos estão em UTF-8 com mojibake legado.
    try:
        return value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", _text(value).casefold())
    return "".join(char for char in value if not unicodedata.combining(char))


def _money(value: str) -> str:
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def search_products(query: str, max_price: float | None = None, available_only: bool = True) -> dict:
    products = _read_csv("products")
    categories = {row["category_id"]: _text(row["name"]) for row in _read_csv("categories")}
    promotions = {
        row["product_id"]: row
        for row in _read_csv("promotions")
        if row.get("is_active", "").strip().casefold() in {"1", "true", "yes"}
    }
    terms = [term for term in _normalize(query).split() if len(term) > 2]
    results = []
    for row in products:
        if row.get("status", "").casefold() != "active":
            continue
        stock = int(row.get("stock_quantity") or 0)
        if available_only and stock <= 0:
            continue
        price = float(row["price_brl"])
        if max_price is not None and price > max_price:
            continue
        name = _text(row["name"])
        category = categories.get(row["category_id"], "Instrumento musical")
        searchable = _normalize(f"{name} {category} {_text(row.get('description', ''))}")
        score = sum(1 for term in terms if term in searchable)
        if not terms or score:
            results.append((score, row, name, category, stock, price))
    results.sort(key=lambda item: (item[0], item[4], -item[5]), reverse=True)
    items = []
    for _, row, name, category, stock, price in results[:8]:
        item = {
            "name": name,
            "category": category,
            "price": _money(str(price)),
            "stock_quantity": stock,
            "description": _text(row.get("description", "")),
        }
        promotion = promotions.get(row["product_id"])
        if promotion:
            discount = float(promotion["discount_percent"])
            item["promotion"] = {
                "description": _text(promotion["description"]),
                "discount_percent": discount,
                "original_price": _money(str(price)),
                "promotional_price": _money(str(price * (1 - discount / 100))),
            }
        items.append(item)
    return {"found": bool(items), "count": len(items), "products": items}


def get_order_status(order_id: str, customer_identifier: str) -> dict:
    orders = _read_csv("orders")
    customers = _read_csv("customers")
    order = next((row for row in orders if row["order_id"].strip() == str(order_id).strip()), None)
    if not order:
        return {"found": False, "message": "Pedido não localizado. Confira o número informado."}
    customer = next((row for row in customers if row["customer_id"] == order["customer_id"]), None)
    if not customer:
        return {"found": False, "message": "Não foi possível validar o cadastro associado ao pedido."}
    supplied_email = customer_identifier.strip().casefold()
    supplied_phone = re.sub(r"\D", "", customer_identifier)
    email = customer.get("email", "").strip().casefold()
    phone = re.sub(r"\D", "", customer.get("phone", ""))
    if not supplied_email or (supplied_email != email and supplied_phone != phone):
        return {"found": False, "message": "Os dados não conferem. Peça ao cliente que confira o número do pedido e o telefone ou e-mail cadastrado."}
    return {
        "found": True,
        "order_id": order["order_id"],
        "status": order["status"],
        "estimated_delivery": order.get("estimated_delivery") or None,
        "tracking_code": order.get("tracking_code") or None,
        "status_note": _text(order.get("notes", "")) or None,
    }
