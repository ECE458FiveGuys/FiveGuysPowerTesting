from django.test import TestCase

from database.exceptions import RequiredFieldsEmptyException, FieldCombinationNotUniqueException, \
    IllegalAccessException, NoSuchEntryExistsException
from database.models import Model, User
from database.services.model_services.create_model import CreateModel
from database.services.model_services.edit_model import EditModel


class EditModelTestCase(TestCase):

    def test_edit_model_without_required_fields_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        try:
            EditModel(user=user, model_id=model.id, vendor=None, model_number=None, description=None).execute()
            self.fail("model without required fields was created")
        except RequiredFieldsEmptyException as e:
            if e.message != "vendor and model_number are required fields for model":
                message = "incorrect error message thrown: {}".format(e.message)
                self.fail(message)
            pass

    def test_edit_model_non_unique_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        try:
            EditModel(user=user, model_id=model.id, vendor="vendor", model_number="model_number",
                      description="description").execute()
        except FieldCombinationNotUniqueException as e:
            if e.message != "The combination of vendor and model_number must be unique for model":
                self.fail("incorrect error message thrown: {}".format(e.message))
            pass

    def test_edit_model_not_admin_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=False)
        try:
            EditModel(user=user, model_id=1, vendor="vendor", model_number="model_number", description="description").execute()
            self.fail("non admin permitted to use function")
        except IllegalAccessException:
            pass

    def test_edit_unexisting_model_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        try:
            EditModel(user=user, model_id=model.id + 1, vendor="vendor", model_number="model_number", description="description").execute()
            self.fail("No model of this id exists")
        except NoSuchEntryExistsException:
            pass

    def test_create_model_succeeds(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        EditModel(user=user, model_id=model.id, vendor="vendor", model_number="model_number", description="description").execute()
        pass


