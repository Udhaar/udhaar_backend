from django.urls import path
from . import views

app_name = "transaction"


urlpatterns = [
    path("", views.TransactionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name="transaction")
]
