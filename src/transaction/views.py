from rest_framework import (viewsets,
                            authentication,
                            permissions,
                            status,
                            response,
                            )
from core.models import StatusChoices, Transaction, User
from .serializers import (TransactionSerializer,
                          TransactionCreateSerializer,
                          TransactionUpdateSerializer)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.filter(is_deleted=False).exclude(
        status=StatusChoices.DECLINED.value)
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "external_id"
    http_method_names = ["patch", "get", "post", "delete"]

    def get_serializer_class(self):
        if self.action == "create":
            return TransactionCreateSerializer
        if self.action == "partial_update":
            return TransactionUpdateSerializer
        return TransactionSerializer

    def get_queryset(self):
        if self.action == "list":
            user1 = self.request.user
            user2 = User.objects.get(
                external_id=self.request.query_params.get("user_external_id"))
            return self.queryset.filter(payer=user1, receiver=user2).union(
                self.queryset.filter(payer=user2, receiver=user1)
            )
        else:
            return super().get_queryset()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user_external_id",
                openapi.IN_QUERY,
                description="external id of user to know balance with",
                type="str"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        user1 = self.request.user
        user2 = User.objects.get(
            external_id=request.query_params.get("user_external_id"))
        if user1.id == user2.id:
            return response.Response({
                "error": "Cannot query transaction with yourself!"
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.paginate_queryset(
            self.get_queryset().order_by("-created_date"))
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

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

    def destroy(self, request, *args, **kwargs):
        transaction: Transaction = self.get_object()
        if (transaction.status == StatusChoices.PENDING.value
                and transaction.created_by.id == request.user.id):
            transaction.is_deleted = True
            transaction.save()
            return response.Response(
                {"success": {"deleted"}},
                status=status.HTTP_200_OK
            )
        return response.Response(
            {"error": {"You cannot delete this transaction"}},
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_update(self, serializer):
        transaction = self.get_object()
        if serializer.validated_data["status"] == StatusChoices.ACCEPTED.value:
            transaction.accept()
        else:
            transaction.decline(
                serializer.validated_data.get("declined_comment")
            )
        serializer.save()
