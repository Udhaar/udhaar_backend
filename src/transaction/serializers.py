from rest_framework.serializers import ValidationError
from rest_framework import serializers
from core.models import Transaction, User
from django.utils.translation import gettext as _
from core.models import StatusChoices


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
        if self.context["view"].action == "create":
            if attrs["receiver"] == attrs["payer"]:
                raise ValidationError(_("You can't transact with yourself"))
        return attrs


class TransactionSerializer(TransactionCreateSerializer):
    class Meta:
        model = Transaction
        exclude = ("id", "is_deleted")
        read_only_fields = ("external_id",)


class TransactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["status", "declined_comment"]

    def validate(self, data):
        if not(
            self.context["request"].user.id != self.instance.created_by.id and
            (self.context["request"].user.id == self.instance.payer.id or
             self.context["request"].user.id == self.instance.receiver.id)
        ):
            raise serializers.ValidationError(
                _("You cannot change this transaction")
            )

        if not data.get("status"):
            raise serializers.ValidationError(
                _("Status is required")
            )

        if data.get("status") == StatusChoices.PENDING.value:
            raise serializers.ValidationError(
                _("You cannot change status to pending.")
            )

        if self.instance.status != StatusChoices.PENDING.value:
            raise serializers.ValidationError(
                _("You can only change status of pending transactions.")
            )

        if data.get("status") == StatusChoices.ACCEPTED.value:
            if data.get("declined_comment"):
                raise serializers.ValidationError(
                    _("Declined comment is not allowed with accepted status.")
                )

        return data
