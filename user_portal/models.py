from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class PowerUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self, username, name, email, password, is_active=True, **extra_fields
    ):
        if not username:
            raise ValueError("The given username must be set")
        if not name:
            raise ValueError("The given name must be set")
        if not email:
            raise ValueError("The given email must be set")
        if not password:
            raise ValueError("The given password must be set")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, name=name, email=email, is_active=is_active, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, email, password, is_active=True, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, name, email, password, is_active, **extra_fields)


class PowerUser(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True, blank=False)
    name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # a admin user; non super-user
    is_superuser = models.BooleanField(default=False)  # a superuser

    objects = PowerUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name", "email", "is_active"]
