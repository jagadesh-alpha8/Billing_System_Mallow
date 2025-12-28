from django.core.management.base import BaseCommand
from shop.models import Product, Denomination

class Command(BaseCommand):
    help = "Seed initial products and denominations"

    def handle(self, *args, **options):
        products = [
            {"name": "Notebook", "product_id": "NB001", "stock": 100, "unit_price": 50.00, "tax_percent": 5.00},
            {"name": "Pen", "product_id": "PEN01", "stock": 200, "unit_price": 10.00, "tax_percent": 12.00},
            {"name": "Backpack", "product_id": "BP01", "stock": 50, "unit_price": 1200.00, "tax_percent": 18.00},
        ]
        for p in products:
            Product.objects.update_or_create(product_id=p["product_id"], defaults=p)
        self.stdout.write(self.style.SUCCESS("Seeded products"))

        denoms = [
            {"value": 500, "count_available": 10},
            {"value": 50,  "count_available": 20},
            {"value": 20,  "count_available": 30},
            {"value": 10,  "count_available": 50},
            {"value": 5,   "count_available": 100},
            {"value": 2,   "count_available": 200},
            {"value": 1,   "count_available": 300},
        ]
        for d in denoms:
            Denomination.objects.update_or_create(value=d["value"], defaults=d)
        self.stdout.write(self.style.SUCCESS("Seeded denominations"))
