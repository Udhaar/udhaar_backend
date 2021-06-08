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
    lookup_field = "external_id"

    def get_serializer_class(self):
        if self.action == "create":
            return TransactionCreateSerializer
        return TransactionSerializer

    def get_queryset(self):
        if self.action == "list":
            user1 = self.request.user
            user2 = User.objects.get(
                external_id=self.request.query_params.get("user"))
            return self.queryset.filter(payer=user1, receiver=user2).union(
                self.queryset.filter(payer=user2, receiver=user1)
            )
        else:
            return super().get_queryset()

    def list(self, request, *args, **kwargs):
        user1 = self.request.user
        user2 = User.objects.get(
            external_id=request.query_params.get("user"))
        if user1.id == user2.id:
            return response.Response({
                "error": "Cannot query transaction with yourself!"
            }, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

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
        request.data["created_by"] = str(current_user.external_id)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        transaction = self.get_object()
        if not (self.request.user.id != transaction.created_by.id and
                (self.request.user.id == transaction.payer.id or
                 self.request.user.id == transaction.receiver.id)):
            return response.Response({
                "error": {
                    "You cannot change this transaction"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        # print(self.get_object())
        for key in request.data.keys():
            if key not in {"status", "declined_comment"}:
                return response.Response({
                    "error": {
                        "Only status and declined_comment can be changed"
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)
