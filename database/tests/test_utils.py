import random
import string
from enum import Enum

from django.test import TestCase
from django.utils.timezone import localtime, now
from rest_framework.test import APIRequestFactory

from database.models import Instrument, CalibrationEvent, EquipmentModel
from user_portal.models import PowerUser

TEST_ROOT = "http://127.0.0.1:8000/"
OVERLONG_STRING = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2001))


def create_model_and_instrument():
    model = create_model()
    instrument = Instrument.objects.create(model=model, serial_number="serial_number")
    return model, instrument


def create_model():
    model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description")
    return model


def create_calibration_events():
    user = create_non_admin_user()
    model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description",
                                 comment="comment", calibration_frequency=1)
    instrument = Instrument.objects.create(model=model, serial_number="serial_number")
    latest = localtime(now()).date()
    later = localtime(now()).date().replace(year=latest.year - 1)
    earlier = localtime(now()).date().replace(year=latest.year - 2)
    calibration_event3 = CalibrationEvent.objects.create(instrument=instrument, user=user, date=latest)
    calibration_event = CalibrationEvent.objects.create(instrument=instrument, user=user, date=earlier)
    calibration_event2 = CalibrationEvent.objects.create(instrument=instrument, user=user, date=later)
    return calibration_event, calibration_event2, calibration_event3, user, model, instrument


def create_3_instruments(model, instrument):
    instrument2 = Instrument.objects.create(model=model, serial_number="serial_number2")
    model2 = EquipmentModel.objects.create(vendor="vendor2", model_number="model_number2", description="description2",
                                  comment="comment2", calibration_frequency=2)
    instrument3 = Instrument.objects.create(model=model2, serial_number="serial_number2")
    return instrument, instrument2, instrument3, model, model2


def create_non_admin_user():
    return PowerUser.objects.create(username="username2", name="name", email="user@gmail.com")


class EndpointTestCase(TestCase):
    class Endpoints(Enum):
        MODELS = TEST_ROOT + "models/"
        VENDORS = TEST_ROOT + "vendors?vendor={}"
        INSTRUMENT = TEST_ROOT + "models/"
        EXPORT_MODELS = TEST_ROOT + "export-models/"
        EXPORT_INSTRUMENTS = TEST_ROOT + "export-instruments/"
        EXPORT_ALL = TEST_ROOT + "export/"
        IMPORT_MODELS = TEST_ROOT + "import-models/"
        IMPORT_INSTRUMENTS = TEST_ROOT + "import-instruments/"


        def fill(self, params):
            return self.value.format(*params)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = PowerUser.objects.create_superuser('username', 'admin', 'email', 'DukeECE458', is_active=True)
