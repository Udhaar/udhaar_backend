from rest_framework.views import APIView
from rest_framework import authentication, permissions, status
from core.models import User, OutstandingBalance
from rest_framework.response import Response
from .serializers import BalanceListSerializer


class BalanceView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, external_id):
        payer = request.user
        receiver = User.objects.get(external_id=external_id)
        balance = OutstandingBalance.objects.filter(
            payer=payer,
            receiver=receiver
        ).first()
        if balance:
            return Response(
                {"balance": balance.balance},
                status=status.HTTP_200_OK
            )
        return Response(
            {"balance": 0.0},
            status=status.HTTP_200_OK
        )


class BalanceListView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = OutstandingBalance.objects.filter(
            payer=user).order_by("-balance")

        data = [{
            "user": balance.receiver,
            "balance": balance.balance
        } for balance in queryset]

        balances = BalanceListSerializer(data=data, many=True)
        balances.is_valid()

        return Response(
            data=balances.data,
            status=status.HTTP_200_OK
        )
