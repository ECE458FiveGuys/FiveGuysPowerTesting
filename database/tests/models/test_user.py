from django.db import IntegrityError
from django.test import TestCase
from database.models import User


class UserTestCase(TestCase):

    # Integrity Tests

    def test_blank_username(self):
        try:
            User.objects.create(password="password", name="name", email="user@gmail.com", admin=True)
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    def test_blank_password(self):
        try:
            User.objects.create(username="username", name="name", email="user@gmail.com", admin=True)
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    def test_blank_name(self):
        try:
            User.objects.create(username="username", password="password", email="user@gmail.com", admin=True)
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    def test_blank_email(self):
        try:
            User.objects.create(username="username", password="password", name="name", admin=True)
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    def test_blank_admin_field(self):
        try:
            User.objects.create(username="username", password="password", name="name", email="user@gmail.com")
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass