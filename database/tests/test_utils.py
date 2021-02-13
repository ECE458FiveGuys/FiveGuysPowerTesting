import random
import string
from enum import Enum

from django.test import TestCase
from django.utils.timezone import localtime, now
from rest_framework.test import APIRequestFactory

from database.models import Instrument, CalibrationEvent, EquipmentModel
from user_portal.models import PowerUser


OVERLONG_STRING = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2001))


def create_model_and_instrument():
    model = create_model()
    instrument = Instrument.objects.create(model=model, serial_number="serial_number")
    return model, instrument


def create_model(calibration_freq=None):
    if calibration_freq is None:
        model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description")
    else:
        model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description", calibration_frequency=calibration_freq)
    return model


def create_calibration_events():
    user = create_non_admin_user()
    model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description",
                                 comment="comment", calibration_frequency=1)
    instrument = Instrument.objects.create(model=model, serial_number="serial_number")
    latest = localtime(now()).date()
    latest = localtime(now()).date().replace(year=latest.year - 1)
    later = localtime(now()).date().replace(year=latest.year - 2)
    earlier = localtime(now()).date().replace(year=latest.year - 3)
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
