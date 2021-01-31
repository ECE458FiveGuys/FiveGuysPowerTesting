from django.test import TestCase

from database.exceptions import RequiredFieldsEmptyException, FieldCombinationNotUniqueException, IllegalAccessException
from database.models import Model, User
from database.services.model_services.create_model import CreateModel


class CreateModelTestCase(TestCase):

    def test_create_model_without_required_fields_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        try:
            CreateModel(user=user, vendor=None, model_number=None, description=None).execute()
            self.fail("model without required fields was created")
        except RequiredFieldsEmptyException as e:
            if e.message != "vendor and model_number are required fields for model":
                message = "incorrect error message thrown: {}".format(e.message)
                self.fail(message)
            pass

    def test_create_model_non_unique_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        try:
            CreateModel(user=user, vendor="vendor", model_number="model_number", description="description").execute()
        except FieldCombinationNotUniqueException as e:
            if e.message != "The combination of vendor and model_number must be unique for model":
                self.fail("incorrect error message thrown: {}".format(e.message))
            pass

    def test_create_model_not_admin_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=False)
        try:
            CreateModel(user=user, vendor="vendor", model_number="model_number", description="description").execute()
            self.fail("non admin permitted to use function")
        except IllegalAccessException:
            pass

    def test_create_model_succeeds(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        CreateModel(user=user, vendor="vendor", model_number="model_number", description="description").execute()
        pass

