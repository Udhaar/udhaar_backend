from rest_framework import serializers
from user.serializers import UserSerializer


class BalanceListSerializer(serializers.Serializer):
    user = UserSerializer()
    balance = serializers.DecimalField(
        max_digits=50,
        decimal_places=2,
    )
