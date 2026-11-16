import re

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("E-posta adresi zorunludur.")
        user = self.model(email=self.normalize_email(email).lower(), username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email).lower()
        self.username = self.username.lower()
        if not re.fullmatch(r"[a-zA-Z0-9_]{3,20}", self.username):
            raise ValidationError({"username": "Kullanıcı adı 3–20 karakter olmalı; harf, rakam ve alt çizgi içerebilir."})

    class Meta:
        constraints = [models.UniqueConstraint(models.functions.Lower("username"), name="accounts_username_lower_unique")]
