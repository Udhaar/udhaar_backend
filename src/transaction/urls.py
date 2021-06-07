from django.urls import path
from . import views

app_name = "transaction"

transaction_list = views.TransactionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = [
    # path("create/",
    #      views.TransactionViewSet.as_view({'list': 'list', 'create': 'create'}), name='create'),
    # path("list/",
    #      views.TransactionViewSet.as_view({'get': 'list', 'create': 'create'}), name='list'),
    path('', transaction_list, name="list"),
    path('create/', transaction_list, name="create"),
    path('<int:user2>/<int:user1>', transaction_list, name="list"),
]
