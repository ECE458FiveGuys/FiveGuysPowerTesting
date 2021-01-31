from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from database.exceptions import IllegalAccessException, NoSuchEntryExistsException
from database.models import Model, User
from database.services.model_services.delete_model import DeleteModel


class DeleteModelTestCase(TestCase):

    def test_delete_models_succeeds(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        DeleteModel(model_id=model.id, user=user).execute()
        try:
            Model.objects.get(id=model.id)
            self.fail("Model did not delete")
        except ObjectDoesNotExist:
            pass

    def test_delete_models_not_admin_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=False)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        try:
            DeleteModel(model_id=model.id, user=user).execute()
            self.fail("non admin was allowed to delete")
        except IllegalAccessException:
            pass

    def test_delete_models_invalid_id_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        try:
            DeleteModel(model_id=model.id + 1, user=user).execute()
            self.fail("delete worked for invalid id")
        except NoSuchEntryExistsException:
            pass
