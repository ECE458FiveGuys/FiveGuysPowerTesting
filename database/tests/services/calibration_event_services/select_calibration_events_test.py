from datetime import datetime, time

from django.test import TestCase

from database.models import Model, Instrument, CalibrationEvent
from database.tests.services.service_test_utils import create_non_admin_user


class SelectCalibrationEventsTestCase(TestCase):

    def test_select_all_instruments(self):
        self.create_3_instruments()
        instruments = SelectInstruments().execute()
        if instruments.count() != 3:
            self.fail("selected wrong instruments")

    def test_select_model_by_instrument_id(self):
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(instrument_id=instrument.id).execute()
        if instruments.count() != 1 or instruments.get(id=instrument.id) != instrument:
            self.fail("selected wrong instrument")

    def test_select_model_by_serial_number(self):
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(serial_number=instrument2.serial_number).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument2.id) != instrument2 or \
                instruments.get(id=instrument3.id) != instrument3:
            self.fail("selected wrong instrument")

    def test_select_model_by_model_id(self):
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(model_id=instrument.model_id).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument.id) != instrument or \
                instruments.get(id=instrument2.id) != instrument2:
            self.fail("selected wrong instrument")

    def test_select_model_by_model_number(self):
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(model_number=model.model_number).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument.id) != instrument or \
                instruments.get(id=instrument2.id) != instrument2:
            self.fail("selected wrong instrument")

    def test_select_model_by_vendor(self):
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(vendor=model.vendor).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument.id) != instrument or \
                instruments.get(id=instrument2.id) != instrument2:
            self.fail("selected wrong instrument")

    def test_select_model_by_description(self):
        instrument, instrument2, instrument3, model, model2 = self.create_3_instruments()
        instruments = SelectInstruments(description=model.description).execute()
        if instruments.count() != 2 or \
                instruments.get(id=instrument.id) != instrument or \
                instruments.get(id=instrument2.id) != instrument2:
            self.fail("selected wrong instrument")


    def create_calibration_events(self):
        user = create_non_admin_user()
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                             comment="comment", calibration_frequency=1)
        instrument = Instrument.objects.create(model=model, serial_number="serial_number")
        earlier = datetime.now()
        time.sleep(1)
        later = datetime.now()
        calibration_event = CalibrationEvent.objects.create(instrument=instrument, user=user, date=earlier)
        calibration_event = CalibrationEvent.objects.create(instrument=instrument, user=user, date=later)

        return instrument,  model, model2
