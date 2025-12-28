from decimal import Decimal
from django.test import TestCase
from .models import Product, Denomination
from .services import validate_and_fetch_products, compute_items, compute_change

class BillingTests(TestCase):
    def setUp(self):
        Product.objects.create(name="ItemA", product_id="A", stock=10, unit_price=100, tax_percent=10)
        Product.objects.create(name="ItemB", product_id="B", stock=5, unit_price=50, tax_percent=5)
        Denomination.objects.create(value=500, count_available=2)
        Denomination.objects.create(value=50, count_available=5)
        Denomination.objects.create(value=20, count_available=5)
        Denomination.objects.create(value=10, count_available=5)
        Denomination.objects.create(value=5, count_available=5)
        Denomination.objects.create(value=2, count_available=5)
        Denomination.objects.create(value=1, count_available=5)

    def test_compute_flow(self):
        lines = [{"product_id": "A", "quantity": 2}, {"product_id": "B", "quantity": 1}]
        pqs = validate_and_fetch_products(lines)
        items, twt, tt, net, rdn = compute_items(pqs)
        self.assertGreater(net, 0)
        # Pay a bit more than rounded total
        change_due, breakdown = compute_change(rdn, Decimal("1000"))
        self.assertGreaterEqual(change_due, 0)
        self.assertTrue(len(breakdown) > 0)
