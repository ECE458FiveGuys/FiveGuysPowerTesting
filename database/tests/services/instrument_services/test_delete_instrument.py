from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from database.exceptions import IllegalAccessException, EntryDoesNotExistException
from database.models import Model, User, Instrument
from database.services.instrument_services.delete_instrument import DeleteInstrument
from database.tests.services.service_test_utils import create_admin_and_model_and_instrument, create_admin_and_model, \
    create_non_admin_user


class DeleteInstrumentTestCase(TestCase):

    def test_delete_models_succeeds(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        DeleteInstrument(instrument_id=instrument.id, user_id=user.id, password=user.password).execute()
        try:
            Instrument.objects.get(id=instrument.id)
            self.fail("Instrument did not delete")
        except ObjectDoesNotExist:
            pass

    def test_delete_models_not_admin_throws_exception(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        non_admin = create_non_admin_user()
        try:
            DeleteInstrument(instrument_id=instrument.id, user_id=non_admin.id, password=non_admin.password).execute()
            self.fail("non admin was allowed to delete")
        except IllegalAccessException:
            pass

    def test_delete_models_invalid_id_throws_exception(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        try:
            DeleteInstrument(instrument_id=instrument.id + 1, user_id=user.id, password=user.password).execute()
            self.fail("delete worked for invalid id")
        except EntryDoesNotExistException:
            pass
