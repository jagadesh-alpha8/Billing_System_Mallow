from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import BillingForm
from .models import Purchase, Denomination, PurchaseChange, CustomerDenomination
from .services import (
    validate_and_fetch_products,
    compute_items,
    compute_change,
    persist_purchase,
)
from .emails import send_invoice_async


@require_http_methods(["GET", "POST"])
def billing_form(request):
    if request.method == "GET":
        form = BillingForm()
        denoms = Denomination.objects.all().order_by("-value")
        return render(request, "billing_form.html", {"form": form, "denoms": denoms})

    form = BillingForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please correct the form errors.")
        denoms = Denomination.objects.all().order_by("-value")
        return render(request, "billing_form.html", {"form": form, "denoms": denoms})

    customer_email = form.cleaned_data["customer_email"]

    # ---------------------------------------------------
    # 1️⃣ Compute cash_paid ONLY (NO STOCK UPDATE HERE)
    # ---------------------------------------------------
    denom_fields = {"d500":500,"d100":100,"d50":50,"d20":20,"d10":10,"d5":5,"d2":2,"d1":1}
    cash_paid = 0
    customer_breakdown = []

    for field, value in denom_fields.items():
        count = int(request.POST.get(field, 0))
        if count > 0:
            cash_paid += count * value
            customer_breakdown.append({"value": value, "count": count})

    cash_paid = Decimal(cash_paid)

    # ---------------------------------------------------
    # 2️⃣ Extract product lines
    # ---------------------------------------------------
    product_ids = request.POST.getlist("product_id[]")
    quantities = request.POST.getlist("quantity[]")

    if not product_ids or not quantities or len(product_ids) != len(quantities):
        messages.error(request, "Add at least one product line.")
        denoms = Denomination.objects.all().order_by("-value")
        return render(request, "billing_form.html", {"form": form, "denoms": denoms})

    lines = []
    try:
        for pid, qty in zip(product_ids, quantities):
            if pid.strip():
                lines.append({"product_id": pid, "quantity": int(qty)})
        if not lines:
            raise ValueError
    except Exception:
        messages.error(request, "Invalid product lines.")
        denoms = Denomination.objects.all().order_by("-value")
        return render(request, "billing_form.html", {"form": form, "denoms": denoms})

    try:
        products_with_qty = validate_and_fetch_products(lines)
        items, total_without_tax, total_tax, net_total, rounded_down_net_total = compute_items(products_with_qty)

        # ---------------------------------------------------
        # 3️⃣ Compute change
        # ---------------------------------------------------
        change_due, breakdown = compute_change(rounded_down_net_total, cash_paid)

        # ---------------------------------------------------
        # 4️⃣ Persist Purchase
        # ---------------------------------------------------
        purchase = persist_purchase(
            customer_email=customer_email,
            cash_paid=cash_paid,
            items_data=items,
            totals=(items, total_without_tax, total_tax, net_total, rounded_down_net_total),
            change_data=(change_due, breakdown),
        )

        # ---------------------------------------------------
        # 5️⃣ Save CUSTOMER denominations + UPDATE STOCK (ONCE)
        # ---------------------------------------------------
        for field, value in denom_fields.items():
            count = int(request.POST.get(field, 0))
            if count > 0:
                CustomerDenomination.objects.create(
                    purchase=purchase,
                    denomination_value=value,
                    count_given=count
                )

                denom, _ = Denomination.objects.get_or_create(
                    value=value, defaults={"count_available": 0}
                )
                denom.count_available += count
                denom.save(update_fields=["count_available"])

        # ---------------------------------------------------
        # 6️⃣ Save SHOP change + DECREMENT STOCK
        # ---------------------------------------------------
        for denom, used in breakdown:
            PurchaseChange.objects.create(
                purchase=purchase,
                denomination_value=denom.value,
                count_returned=used
            )
            denom.count_available -= used
            denom.save(update_fields=["count_available"])

    except Exception as e:
        messages.error(request, str(e))
        denoms = Denomination.objects.all().order_by("-value")
        return render(request, "billing_form.html", {"form": form, "denoms": denoms})

    try:
        send_invoice_async(purchase)
    except Exception:
        pass

    request.session["customer_breakdown"] = customer_breakdown
    return redirect("shop:bill_summary", purchase_id=purchase.id)

def bill_summary(request, purchase_id: int):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    # Fetch persisted denominations
    customer_denoms = CustomerDenomination.objects.filter(purchase=purchase).order_by("-denomination_value")
    return render(request,"bill_summary.html",{"purchase": purchase, "customer_denoms": customer_denoms})

def purchases_list(request):
    email = request.GET.get("email", "").strip()
    purchases = Purchase.objects.none()
    if email:
        purchases = Purchase.objects.filter(customer_email=email).order_by("-created_at")
    return render(request, "purchases_list.html", {"email": email, "purchases": purchases})

def purchase_detail(request, purchase_id: int):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    customer_denoms = CustomerDenomination.objects.filter(purchase=purchase).order_by("-denomination_value")
    return render(request,"purchase_detail.html",{"purchase": purchase, "customer_denoms": customer_denoms})
