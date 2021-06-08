from rest_framework.serializers import ValidationError
from rest_framework import serializers
from core.models import Transaction, User
from django.utils.translation import gettext as _


class TransactionCreateSerializer(serializers.ModelSerializer):
    payer = serializers.SlugRelatedField(
        slug_field="external_id", queryset=User.objects.all())
    receiver = serializers.SlugRelatedField(
        slug_field="external_id", queryset=User.objects.all())
    created_by = serializers.SlugRelatedField(
        slug_field="external_id", queryset=User.objects.all())

    class Meta:
        model = Transaction
        fields = ["payer", "receiver", "created_by",
                  "amount", "message", "external_id"]
        read_only_fields = ("external_id",)

    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError(
                _("Amount must br greater than zero")
            )
        return value

    def validate(self, attrs):
        # print(self.context["view"].action)
        if self.context["view"].action == "create":
            if attrs["receiver"] == attrs["payer"]:
                raise ValidationError(_("You can't transact with yourself"))
        return attrs


class TransactionSerializer(TransactionCreateSerializer):
    class Meta:
        model = Transaction
        exclude = ("id", "is_deleted")
        read_only_fields = ("external_id",)
