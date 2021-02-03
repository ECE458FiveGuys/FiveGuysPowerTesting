from datetime import datetime, time

from django.test import TestCase

from database.models import Model, Instrument, CalibrationEvent
from database.tests.services.service_test_utils import create_non_admin_user


class SelectCalibrationEventsTestCase(TestCase):

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
