from django.db import IntegrityError
from django.db.models.functions import datetime
from django.test import TestCase
from database.models import Model, User, CalibrationEvent
from database.models import Instrument


class CalibrationEventTestCase(TestCase):

    def create_objects(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                                     comment="comment", calibration_frequency=1)
        instrument = Instrument.objects.create(model=model, serial_number="serial_number", comment="comment")
        return user, instrument

    def test_optional_fields_empty_no_exception(self):
        user, instrument = self.create_objects()
        try:
            CalibrationEvent.objects.create(instrument=instrument, user=user, date=datetime.Now())
            pass
        except Exception:
            self.fail("optional fields throwing error")

    def test_optional_fields_none_no_exception(self):
        user, instrument = self.create_objects()
        try:
            CalibrationEvent.objects.create(instrument=instrument, user=user, date=datetime.Now(), comment=None)
            pass
        except Exception:
            self.fail("optional fields throwing error")

    def test_blank_user(self):
        user, instrument = self.create_objects()
        try:
            CalibrationEvent.objects.create(instrument=instrument, date=datetime.Now(), comment="comment")
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    def test_blank_instrument(self):
        user, instrument = self.create_objects()
        try:
            CalibrationEvent.objects.create(user=user, date=datetime.Now(), comment="comment")
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass

    def test_blank_date(self):
        user, instrument = self.create_objects()
        try:
            CalibrationEvent.objects.create(instrument=instrument, user=user, comment="comment")
            self.fail("NON NULL field allowed")
        except IntegrityError:
            pass