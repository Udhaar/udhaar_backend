from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import uuid
from django.utils import timezone


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
    objects = UserManager()
    USERNAME_FIELD = "email"

    def save(self, *args, **kwargs):
        self.last_modified_date = timezone.now()
        super(User, self).save(*args, **kwargs)
