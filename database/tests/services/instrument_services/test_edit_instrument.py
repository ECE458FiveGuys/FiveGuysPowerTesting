from django.test import TestCase

from database.exceptions import RequiredFieldsEmptyException, FieldCombinationNotUniqueException, \
    IllegalAccessException, EntryDoesNotExistException
from database.models import Model, User, Instrument
from database.services.instrument_services.create_instrument import CreateInstrument
from database.services.instrument_services.edit_instrument import EditInstrument
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.model_services.create_model import CreateModel
from database.tests.services.service_test_utils import create_admin_and_model_and_instrument, create_admin_and_model

class EditInstrumentTestCase(TestCase):

    def test_edit_instrument_happy_case(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        EditInstrument(user=user, instrument_id=instrument.id, model_id=model.id, serial_number="serial_number_2").execute()
        instruments = SelectInstruments(instrument_id=instrument.id).execute()
        if instruments.count() != 1 or instruments.get(id=instrument.id).serial_number != "serial_number_2":
            self.fail("selected wrong instrument")

    def test_edit_instrument_invalid_model_id_exception(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        try:
            EditInstrument(user=user, instrument_id=instrument.id, model_id=model.id + 1, serial_number="serial_number").execute()
            self.fail("instrument with invalid model id allowed to be edited")
        except EntryDoesNotExistException as e:
            expected_message = "The model with id {} no longer exists".format(model.id + 1)
            if e.message == expected_message:
                pass
            else:
                self.fail("Incorrect error message.\n Actual: {} \n Expected: {}".format(e.message, expected_message))

    def test_edit_instrument_invalid_instrument_id_exception(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        try:
            EditInstrument(user=user, instrument_id=instrument.id + 1, model_id=model.id, serial_number="serial_number").execute()
            self.fail("instrument with invalid instrument id allowed to be edited")
        except EntryDoesNotExistException as e:
            expected_message = "The instrument with id {} no longer exists".format(instrument.id + 1)
            if e.message == expected_message:
                pass
            else:
                self.fail("Incorrect error message.\n Actual: {} \n Expected: {}".format(e.message, expected_message))

    def test_edit_instrument_without_required_fields_throws_exception(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        try:
            EditInstrument(user=user, instrument_id=None, model_id=None, serial_number=None).execute()
            self.fail("instrument without required fields was edited")
        except RequiredFieldsEmptyException as e:
            if e.message != "model and serial_number are required fields for instrument":
                message = "incorrect error message thrown: {}".format(e.message)
                self.fail(message)
            pass

    # create 2 instruments with same model but different serial numbers, then edit them to make serial numbers identical
    # should throw error bc this violates uniqueness constraint

    def test_edit_instrument_non_unique_throws_exception(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        instrument2 = CreateInstrument(user=user, model_id=model.id, serial_number="serial_number_2").execute()
        try:
            EditInstrument(user=user, instrument_id=instrument2.id, model_id=model.id, serial_number="serial_number").execute()
            self.fail("non unqiue instrument was edited")
        except FieldCombinationNotUniqueException as e:
            if e.message != "The combination of model and serial_number must be unique for instrument":
                self.fail("incorrect error message thrown: {}".format(e.message))
            pass

    def test_edit_instrument_not_admin_throws_exception(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=False)
        try:
            EditInstrument(user=user, instrument_id=instrument.id, model_id=model.id, serial_number="serial_number").execute()
            self.fail("non admin permitted to use function")
        except IllegalAccessException:
            pass