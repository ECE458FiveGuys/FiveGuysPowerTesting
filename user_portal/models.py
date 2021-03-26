from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, Group, PermissionsMixin
from django.db import models

from user_portal.enums import PermissionGroupEnum


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, name, email, password, is_active=True, **extra_fields):
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

    def create_oauth_user(self, username, name, email):
        if not username:
            raise ValueError("The given username must be set")
        if not name:
            raise ValueError("The given name must be set")
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, name=name, email=email, is_active=True)
        user.set_password(self.make_random_password())
        user.save(using=self._db)
        user.groups.add(Group.objects.get(name=PermissionGroupEnum.UNPRIVILEGED.value))
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, email, password, is_active=True, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(username, name, email, password, is_active, **extra_fields)
        user.save(using=self._db)
        return user

    def oauth_users(self):
        return self.filter(username__contains='@')


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, blank=False)
    name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name", "email", "is_active"]

    def __str__(self):
        template = '(Username:{0.username}, Name:{0.name}, Email:{0.email}, Active:{0.is_active})'
        return template.format(self)
