from decimal import Decimal, ROUND_DOWN
from typing import List, Dict, Tuple
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product, Purchase, PurchaseItem, Denomination, PurchaseChange

def round_down(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1."), rounding=ROUND_DOWN)

def validate_and_fetch_products(lines: List[Dict]) -> List[Tuple[Product, int]]:
    resolved = []
    for line in lines:
        pid = line["product_id"].strip()
        qty = int(line["quantity"])
        try:
            product = Product.objects.get(product_id=pid)
        except Product.DoesNotExist:
            raise ValidationError(f"Product ID '{pid}' not found.")
        if product.stock < qty:
            raise ValidationError(f"Insufficient stock for {product.product_id}. Available: {product.stock}, requested: {qty}.")
        resolved.append((product, qty))
    return resolved

def compute_items(products_with_qty: List[Tuple[Product, int]]):
    items = []
    total_without_tax = Decimal("0.00")
    total_tax = Decimal("0.00")

    for product, qty in products_with_qty:
        unit_price = Decimal(str(product.unit_price))
        tax_percent = Decimal(str(product.tax_percent))
        purchase_price = unit_price * qty
        tax_payable = (purchase_price * tax_percent) / Decimal("100")
        total_item = purchase_price + tax_payable

        items.append({
            "product": product,
            "quantity": qty,
            "unit_price": unit_price,
            "tax_percent": tax_percent,
            "purchase_price": purchase_price,
            "tax_payable": tax_payable,
            "total_price_item": total_item,
        })
        total_without_tax += purchase_price
        total_tax += tax_payable

    net_total = total_without_tax + total_tax
    rounded_down_net_total = round_down(net_total)

    return items, total_without_tax, total_tax, net_total, rounded_down_net_total

def compute_change(rounded_total: Decimal, cash_paid: Decimal):
    # Returns remaining balance to return and change breakdown based on Denomination inventory
    if cash_paid < rounded_total:
        raise ValidationError("Cash paid is less than the rounded down net total.")

    change_due = int(cash_paid - rounded_total)
    breakdown = []
    denom_qs = Denomination.objects.all().order_by("-value")
    remaining = change_due

    for denom in denom_qs:
        if remaining <= 0:
            break
        max_needed = remaining // denom.value
        if max_needed <= 0:
            continue
        use = min(max_needed, denom.count_available)
        if use > 0:
            breakdown.append((denom, use))
            remaining -= use * denom.value

    if remaining != 0:
        # Not enough denominations in the shop to make exact change
        raise ValidationError("Insufficient denominations available to return exact change.")

    return change_due, breakdown

@transaction.atomic
def persist_purchase(customer_email: str, cash_paid: Decimal, items_data, totals, change_data):
    items, total_without_tax, total_tax, net_total, rounded_down_net_total = totals
    change_due, breakdown = change_data

    purchase = Purchase.objects.create(
        customer_email=customer_email,
        total_without_tax=total_without_tax,
        total_tax=total_tax,
        net_total=net_total,
        rounded_down_net_total=rounded_down_net_total,
        cash_paid=cash_paid,
        balance_payable=Decimal(str(change_due)),
    )

    # Save items and decrement stock
    for item in items:
        PurchaseItem.objects.create(
            purchase=purchase,
            product=item["product"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            tax_percent=item["tax_percent"],
            purchase_price=item["purchase_price"],
            tax_payable=item["tax_payable"],
            total_price_item=item["total_price_item"],
        )
        # Update stock
        prod = item["product"]
        prod.stock -= item["quantity"]
        prod.save(update_fields=["stock"])
    return purchase
