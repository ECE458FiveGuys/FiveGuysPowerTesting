from django.core.exceptions import ValidationError
from django.test import TestCase

from database.models.instrument import Instrument
from database.tests.test_utils import OVERLONG_STRING, create_model, create_model_and_instrument


class CreateInstrumentTestCase(TestCase):

    def test_create_instrument_happy_case(self):
        model, instrument = create_model_and_instrument()
        instruments = Instrument.objects.all()
        if instruments.count() != 1 or instruments.get(id=instrument.id) != instrument:
            self.fail("selected wrong instrument")

    def test_create_instrument_without_required_fields_throws_exception(self):
        try:
            Instrument.objects.create(model=None, serial_number=None).execute()
            self.fail("instrument without required fields was created")
        except ValidationError:
            pass

    def test_create_instrument_non_unique_throws_exception(self):
        model, instrument = create_model_and_instrument()
        with self.assertRaises(ValidationError):
            Instrument.objects.create(model=model, serial_number="serial_number")

    # Field length tests

    def test_create_instrument_overlong_serial_number(self):
        model = create_model()
        try:
            Instrument.objects.create(model=model, serial_number=OVERLONG_STRING).execute()
            self.fail("overlong serial number permitted")
        except ValidationError:
            pass

    def test_create_instrument_overlong_comment(self):
        model = create_model()
        try:
            Instrument.objects.create(model=model, serial_number="serial_number", comment=OVERLONG_STRING).execute()
            self.fail("overlong comment permitted")
        except ValidationError:
            pass
