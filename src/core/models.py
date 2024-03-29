from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import uuid
from django.utils import timezone
import enum
from decimal import Decimal
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, *args, **kwargs):
        if not email:
            raise ValueError("Users must have email address")

        user = self.model(email=self.normalize_email(email), *args, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, *args, **kwargs):
        user = self.create_user(email, password, *args, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class BaseModel(models.Model):
    external_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_date = models.DateTimeField(auto_now=True)
    last_modified_date = models.DateTimeField(
        default=timezone.now)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(max_length=512, unique=True)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = "email"

    def save(self, *args, **kwargs):
        self.last_modified_date = timezone.now()
        super(User, self).save(*args, **kwargs)

    def name(self):
        return f"{self.first_name} {self.last_name}"


class StatusChoices(enum.Enum):
    PENDING = 1
    ACCEPTED = 2
    DECLINED = 3


STATUS_CHOICES = [(choice.value, choice.name) for choice in StatusChoices]


class Transaction(BaseModel):
    payer = models.ForeignKey(
        User, on_delete=models.PROTECT, null=False,
        blank=False, related_name="payer"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.PROTECT, null=False,
        blank=False, related_name="receiver"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=False,
        blank=False, related_name="created_by"
    )
    amount = models.DecimalField(
        decimal_places=2, null=False, blank=False, max_digits=50
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES, blank=False, null=False, default=1
    )
    declined_comment = models.TextField(null=True, blank=True)
    message = models.TextField(null=False, blank=False)
    is_deleted = models.BooleanField(default=False, null=False, blank=False)

    def save(self, **kwargs) -> None:
        return_value = super().save(**kwargs)

        positive_balance_object = OutstandingBalance.objects.filter(
            payer=self.payer,
            receiver=self.receiver
        ).first()
        if not positive_balance_object:
            OutstandingBalance(
                payer=self.payer,
                receiver=self.receiver,
            ).save()
            OutstandingBalance(
                payer=self.receiver,
                receiver=self.payer,
            ).save()

        return return_value

    def accept(self):
        positive_balance_object = OutstandingBalance.objects.filter(
            payer=self.payer,
            receiver=self.receiver
        ).first()
        negative_balance_object = OutstandingBalance.objects.filter(
            payer=self.receiver,
            receiver=self.payer,
        ).first()
        positive_balance_object.balance += Decimal(self.amount)
        negative_balance_object.balance -= Decimal(self.amount)
        positive_balance_object.save()
        negative_balance_object.save()
        self.status = StatusChoices.ACCEPTED.value
        self.save()

        Notification.objects.filter(
            transaction=self
        ).first().delete()

        Notification.objects.create(
            user=self.created_by,
            notification_type=NotificationTypeChoices.
            ACCEPTED_TRANSACTION.value,
            transaction=self,
        )

    def decline(self, comment):

        self.status = StatusChoices.DECLINED.value
        if comment:
            self.declined_comment = comment
        self.save()

        Notification.objects.filter(
            transaction=self
        ).first().delete()
        Notification.objects.create(
            user=self.created_by,
            notification_type=NotificationTypeChoices.
            DECLINED_TRANSACTION.value,
            transaction=self,
        )

    def __str__(self) -> str:
        return f"Transaction {self.payer.name()} => {self.receiver.name()} : \
{self.amount:.2f}"


class OutstandingBalance(BaseModel):
    payer = models.ForeignKey(
        User,
        related_name="balance_payer",
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )
    receiver = models.ForeignKey(
        User,
        related_name="balance_receiver",
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )
    balance = models.DecimalField(
        decimal_places=2,
        null=False,
        blank=False,
        max_digits=50,
        default=Decimal(0.0)
    )

    def __str__(self) -> str:
        return f"{self.receiver.email} owes {self.payer.email} : \
{self.balance:.2f}"


class NotificationTypeChoices(enum.Enum):
    NEW_RECEIVED_TRANSACTION = "NEW_RECEIVED_TRANSACTION"
    NEW_SENT_TRANSACTION = "NEW_SENT_TRANSACTION"
    ACCEPTED_TRANSACTION = "ACCEPTED_TRANSACTION"
    DECLINED_TRANSACTION = "DECLINED_TRANSACTION"


NOTIFICATION_TYPE_CHOICES = [(choice.value, choice.name)
                             for choice in NotificationTypeChoices]


class Notification(BaseModel):
    user = models.ForeignKey(
        User,
        related_name="user",
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    transaction = models.ForeignKey(
        Transaction, related_name="transaction",
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    is_dismissed = models.BooleanField(
        default=False, null=False
    )
    notification_type = models.CharField(
        choices=NOTIFICATION_TYPE_CHOICES,
        blank=False,
        null=False,
        max_length=255
    )

    def __str__(self) -> str:
        return f"{self.user.email} {self.is_dismissed} \
{self.notification_type}"


@receiver(post_save, sender=Transaction)
def create_notification(sender, instance: Transaction, created, **kwargs):
    if created:
        user = (
            instance.payer
            if
            instance.created_by.id == instance.receiver.id
            else
            instance.receiver
        )
        notification_type = (
            NotificationTypeChoices.NEW_SENT_TRANSACTION
            if
            instance.created_by.id == instance.receiver.id
            else
            NotificationTypeChoices.NEW_RECEIVED_TRANSACTION
        )
        Notification.objects.create(
            user=user,
            notification_type=notification_type.value,
            transaction=instance
        )
