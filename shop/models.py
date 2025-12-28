from django.db import models
from django.core.validators import MinValueValidator

class Product(models.Model):
    name = models.CharField(max_length=255)
    product_id = models.CharField(max_length=64, unique=True)
    stock = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])  # e.g., 18.00

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.product_id})"

class Denomination(models.Model):
    value = models.PositiveIntegerField(unique=True)  # e.g., 500, 50, 20...
    count_available = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-value"]

    def __str__(self):
        return f"{self.value} x {self.count_available}"

class Purchase(models.Model):
    customer_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_without_tax = models.DecimalField(max_digits=12, decimal_places=2)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2)
    net_total = models.DecimalField(max_digits=12, decimal_places=2)
    rounded_down_net_total = models.DecimalField(max_digits=12, decimal_places=2)
    cash_paid = models.DecimalField(max_digits=12, decimal_places=2)
    balance_payable = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Purchase #{self.id} - {self.customer_email}"

class CustomerDenomination(models.Model):
    purchase = models.ForeignKey(Purchase, related_name="customer_denoms", on_delete=models.CASCADE)
    denomination_value = models.PositiveIntegerField()
    count_given = models.PositiveIntegerField()


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)  # unit_price * qty
    tax_payable = models.DecimalField(max_digits=12, decimal_places=2)     # purchase_price * tax%
    total_price_item = models.DecimalField(max_digits=12, decimal_places=2)  # purchase_price + tax

    def __str__(self):
        return f"{self.product.product_id} x {self.quantity}"

class PurchaseChange(models.Model):
    purchase = models.ForeignKey(Purchase, related_name="change_breakdown", on_delete=models.CASCADE)
    denomination_value = models.PositiveIntegerField()
    count_returned = models.PositiveIntegerField()

    class Meta:
        ordering = ["-denomination_value"]
