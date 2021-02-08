from django.test import TestCase

from database.exceptions import UserError, AuthenticationFailedException, InactiveUserException
from database.models import User
from database.services.model_services.select_models import SelectModels


class InAppServiceTestCase(TestCase):

    def test_in_app_service_invalid_user_id(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                               admin=True)
        try:
            SelectModels(user_id=user.id+1, password="password")
        except UserError:
            pass

    def test_in_app_service_invalid_password(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                               admin=True)
        try:
            SelectModels(user_id=user.id, password="password2")
        except AuthenticationFailedException:
            pass

    def test_in_app_service_invalid_password(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                               admin=True, active=False)
        try:
            SelectModels(user_id=user.id, password="password")
        except InactiveUserException:
            pass