from django.contrib import auth
from rest_framework import mixins, viewsets, authentication, permissions
from rest_framework.test import RequestsClient
from core.models import Transaction, User
from .serializers import TransactionSerializer


class TransactionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.filter(is_deleted=False)
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user1 = self.request.user
        user2 = User.objects.get(id=self.kwargs.get("user2"))
        return self.queryset.filter(payer=user1, receiver=user2).union(self.queryset.filter(payer=user2, receiver=user1))

    # def list(self, request, *args, **kwargs):
    #     user2 = kwargs.get("user2")
    #     print(user2)
    #     print(request, args, kwargs)
    #     self.get_queryset()
    #     return self.get_queryset()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
