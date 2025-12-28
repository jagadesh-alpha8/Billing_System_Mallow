from django.contrib import admin
from .models import Product, Denomination, Purchase, PurchaseItem, PurchaseChange, CustomerDenomination

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "product_id", "stock", "unit_price", "tax_percent")
    search_fields = ("name", "product_id")

@admin.register(Denomination)
class DenominationAdmin(admin.ModelAdmin):
    list_display = ("value", "count_available")

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0

class PurchaseChangeInline(admin.TabularInline):
    model = PurchaseChange
    extra = 0

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_email", "created_at", "net_total", "cash_paid", "balance_payable")
    inlines = [PurchaseItemInline, PurchaseChangeInline]
    search_fields = ("customer_email",)

@admin.register(CustomerDenomination)
class CustomerDenominationAdmin(admin.ModelAdmin):
    list_display=("id","purchase","denomination_value","count_given")