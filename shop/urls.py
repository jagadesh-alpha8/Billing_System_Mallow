# shop/urls.py
from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.billing_form, name="billing_form"),
    path("bill/summary/<int:purchase_id>/", views.bill_summary, name="bill_summary"),
    path("purchases/", views.purchases_list, name="purchases_list"),
    path("purchases/<int:purchase_id>/", views.purchase_detail, name="purchase_detail"),
]
