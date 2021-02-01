from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from database.exceptions import IllegalAccessException, EntryDoesNotExistException, UserError
from database.models import Model, User
from database.services.instrument_services.create_instrument import CreateInstrument
from database.services.model_services.delete_model import DeleteModel
from database.tests.services.service_test_utils import create_admin_and_model_and_instrument, create_admin_and_model, \
    create_non_admin_user


class DeleteModelTestCase(TestCase):

    def test_delete_models_happy_case(self):
        user, model = create_admin_and_model()
        DeleteModel(model_id=model.id, user=user).execute()
        try:
            Model.objects.get(id=model.id)
            self.fail("Model did not delete")
        except ObjectDoesNotExist:
            pass

    def test_delete_models_not_admin_throws_exception(self):
        admin, model = create_admin_and_model()
        user = create_non_admin_user()
        try:
            DeleteModel(model_id=model.id, user=user).execute()
            self.fail("non admin was allowed to delete")
        except IllegalAccessException:
            pass

    def test_delete_models_invalid_id_throws_exception(self):
        user, model = create_admin_and_model()
        try:
            DeleteModel(model_id=model.id + 1, user=user).execute()
            self.fail("delete worked for invalid id")
        except EntryDoesNotExistException:
            pass

    def test_delete_models_instrument_exists_throws_exception(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        try:
            DeleteModel(model_id=model.id, user=user).execute()
            self.fail("delete worked even though model exists")
        except UserError as e:
            if e.message == "Cannot be deleted, as instruments of this model exist":
                pass
            else:
                self.fail("incorrect error message")

