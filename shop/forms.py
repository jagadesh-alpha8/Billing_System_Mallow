from django import forms

class ProductLineForm(forms.Form):
    product_id = forms.CharField(max_length=64)
    quantity = forms.IntegerField(min_value=1)

class DenominationForm(forms.Form):
    # Defaults: 500, 50, 20, 10, 5, 2, 1
    d500 = forms.IntegerField(min_value=0, required=False, initial=0, label="500")
    d50  = forms.IntegerField(min_value=0, required=False, initial=0, label="50")
    d20  = forms.IntegerField(min_value=0, required=False, initial=0, label="20")
    d10  = forms.IntegerField(min_value=0, required=False, initial=0, label="10")
    d5   = forms.IntegerField(min_value=0, required=False, initial=0, label="5")
    d2   = forms.IntegerField(min_value=0, required=False, initial=0, label="2")
    d1   = forms.IntegerField(min_value=0, required=False, initial=0, label="1")

class BillingForm(forms.Form):
    customer_email = forms.EmailField()
    cash_paid = forms.DecimalField(min_value=0, decimal_places=2, max_digits=12)

    # Dynamic product lines handled with JS and request.POST arrays

    def clean(self):
        cleaned = super().clean()
        return cleaned
