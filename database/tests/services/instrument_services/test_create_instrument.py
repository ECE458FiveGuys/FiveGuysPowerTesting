from django.test import TestCase

from database.exceptions import RequiredFieldsEmptyException, FieldCombinationNotUniqueException, \
    IllegalAccessException, EntryDoesNotExistException
from database.models import EquipmentModel, User, Instrument
from database.services.instrument_services.create_instrument import CreateInstrument
from database.services.instrument_services.select_instruments import SelectInstruments
from database.tests.services.service_test_utils import create_admin_and_model_and_instrument, create_admin_and_model


class CreateInstrumentTestCase(TestCase):

    def test_create_instrument_happy_case(self):
        user, model, instrument = create_admin_and_model_and_instrument()
        instruments = SelectInstruments(user_id=user.id, password=user.password, instrument_id=instrument.id).execute()
        if instruments.count() != 1 or instruments.get(id=instrument.id) != instrument:
            self.fail("selected wrong instrument")

    def test_create_instrument_invalid_model_id_exception(self):
        user, model = create_admin_and_model()
        try:
            CreateInstrument(user_id=user.id, password=user.password, model_id=model.id + 1, serial_number="serial_number").execute()
            self.fail("instrument with invalid model_id allowed to be created")
        except EntryDoesNotExistException as e:
            expected_message = "The model with id {} no longer exists".format(model.id + 1)
            if e.message == expected_message:
                pass
            else:
                self.fail("Incorrect error message.\n Actual: {} \n Expected: {}".format(e.message, expected_message))

    def test_create_instrument_without_required_fields_throws_exception(self):
        user, model = create_admin_and_model()
        try:
            CreateInstrument(user_id=user.id, password=user.password, model_id=None, serial_number=None).execute()
            self.fail("instrument without required fields was created")
        except RequiredFieldsEmptyException as e:
            if e.message != "model and serial_number are required fields for instrument":
                message = "incorrect error message thrown: {}".format(e.message)
                self.fail(message)
            pass

    def test_create_instrument_non_unique_throws_exception(self):
        user, model = create_admin_and_model()
        Instrument.objects.create(model=model, serial_number="serial_number")
        try:
            CreateInstrument(user_id=user.id, password=user.password, model_id=model.id, serial_number="serial_number").execute()
            self.fail("non unqiue instrument was created")
        except FieldCombinationNotUniqueException as e:
            if e.message != "The combination of model and serial_number must be unique for instrument":
                self.fail("incorrect error message thrown: {}".format(e.message))
            pass

    def test_create_instrument_not_admin_throws_exception(self):
        user, model = create_admin_and_model()
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=False)
        try:
            CreateInstrument(user_id=user.id, password=user.password, model_id=model.id, serial_number="serial_number").execute()
            self.fail("non admin permitted to use function")
        except IllegalAccessException:
            pass