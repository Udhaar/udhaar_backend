from rest_framework import serializers

from core.models import Notification
from transaction.serializers import TransactionSerializer


class NotificationSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()

    class Meta:
        model = Notification
        exclude = ["id", "last_modified_date", "user"]
