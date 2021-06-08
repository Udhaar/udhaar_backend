from rest_framework import (viewsets,
                            authentication,
                            permissions,
                            status,
                            response
                            )
from core.models import Transaction, User
from .serializers import TransactionSerializer, TransactionCreateSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.filter(is_deleted=False)
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return TransactionCreateSerializer
        return TransactionSerializer

    def get_queryset(self):
        user1 = self.request.user
        user2 = User.objects.get(id=self.kwargs.get("user2"))
        return self.queryset.filter(payer=user1, receiver=user2).union(
            self.queryset.filter(payer=user2, receiver=user1)
        )

    # def list(self, request, *args, **kwargs):
    #     user2 = kwargs.get("user2")
    #     print(user2)
    #     print(request, args, kwargs)
    #     self.get_queryset()
    #     return self.get_queryset()

    def create(self, request, *args, **kwargs):
        if "receiver" in request.data and "payer" in request.data:
            return response.Response({
                "error": {
                    "Only either payer or receiver is allowed not both"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        current_user: User = request.user
        if "receiver" in request.data:
            request.data["payer"] = str(current_user.external_id)
        elif "payer" in request.data:
            request.data["receiver"] = str(current_user.external_id)
        return super().create(request, *args, **kwargs)
