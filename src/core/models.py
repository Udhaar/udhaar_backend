from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import uuid
from django.utils import timezone
import enum


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
    amount = models.DecimalField(
        decimal_places=2, null=False, blank=False, max_digits=50
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES, blank=False, null=False, default=1
    )
    declined_comment = models.TextField(null=True, blank=True)
    message = models.TextField(null=False, blank=False)
    is_deleted = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self) -> str:
        return f"Transaction {self.payer.name()} => {self.receiver.name()} : \
{self.amount:.2f}"
