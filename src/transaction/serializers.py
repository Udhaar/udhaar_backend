from rest_framework.serializers import ValidationError
from rest_framework import serializers
from core.models import Transaction, User
from django.utils.translation import gettext as _


class TransactionSerializer(serializers.ModelSerializer):
    payer = serializers.SlugRelatedField(
        slug_field="external_id", queryset=User.objects.all())
    receiver = serializers.SlugRelatedField(
        slug_field="external_id", queryset=User.objects.all())

    class Meta:
        model = Transaction
        exclude = ("id", "is_deleted")
        read_only_fields = ("external_id",)

    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError(
                _("Amount must br greater than zero")
            )
        return value

    def validate(self, attrs):
        if attrs["receiver"] == attrs["payer"]:
            raise ValidationError(_("You can't transact with yourself"))
        return attrs
