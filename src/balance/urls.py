from django.urls import path
from . import views

app_name = "balance"

urlpatterns = [
    path("", views.BalanceListView.as_view(), name="balance_list"),
    path("<str:external_id>", views.BalanceView.as_view(), name="get_balance"),
]
