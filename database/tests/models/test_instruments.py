from django.db import IntegrityError
from django.test import TestCase
from database.models import Model
from database.models import Instrument


class InstrumentTestCase(TestCase):
    def test_optional_fields_empty(self):
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                                     comment="comment", calibration_frequency=1)
        try:
            Instrument.objects.create(model=model, serial_number="serial_number")
            pass
        except Exception:
            self.fail("optional fields throwing error")

    def test_blank_model(self):
        try:
            Instrument.objects.create(serial_number="serial_number", comment="comment")
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    def test_blank_serial_num(self):
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                                     comment="comment", calibration_frequency=1)
        try:
            Instrument.objects.create(model=model, comment="comment")
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    # Other tests

    def test_is_calibratable(self):
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                                     comment="comment", calibration_frequency=1)
        instrument = Instrument.objects.create(model=model, serial_number="serial_number", comment="comment")
        assert instrument.is_calibratable()
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                                     comment="comment")
        instrument = Instrument.objects.create(model=model, serial_number="serial_number", comment="comment")
        assert not instrument.is_calibratable()