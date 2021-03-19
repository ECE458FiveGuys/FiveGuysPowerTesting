from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from database.exceptions import RequiredFieldsEmptyException
from database.models.instrument import CalibrationEvent, Instrument
from database.tests.test_utils import OVERLONG_STRING, create_model_and_instrument, create_non_admin_user


class CreateCalibrationEventTestCase(TestCase):
    def test_create_calib_happy_case(self):
        model, instrument = create_model_and_instrument(10)
        user = create_non_admin_user()
        date = datetime.today().astimezone()
        c1 = CalibrationEvent.objects.create(user=user, instrument=instrument, date=date.replace(year=date.year - 1))
        c2 = CalibrationEvent.objects.get(user=user)
        self.assertEqual(c1, c2)

    def test_create_instrument_without_required_fields_throws_exception(self):
        try:
            CalibrationEvent.objects.create(user=None, instrument=None, date=None)
            self.fail("calibration event without required fields was created")
        except Instrument.DoesNotExist:
            return
        except RequiredFieldsEmptyException as e:
            if e.message != "Error: instrument id and user and date are required fields for the calibration event " \
                            "with vendor 'None' and model number 'None' and serial number 'None' and date 'None'":
                message = "incorrect error message thrown: {}".format(e.message)
                self.fail(message)
            pass

    # Field validity tests

    def test_overlong_comment_field_test(self):
        model, instrument = create_model_and_instrument()
        user = create_non_admin_user()
        date = datetime.today().astimezone()
        try:
            CalibrationEvent.objects.create(instrument=instrument, user=user, comment=OVERLONG_STRING,
                                            date=date.replace(year=date.year - 1))
            self.fail("overlong comment allowed")
        except ValidationError:
            pass

    def test_invalid_date_field_test(self):
        model, instrument = create_model_and_instrument()
        user = create_non_admin_user()
        try:
            CalibrationEvent.objects.create(instrument=instrument, user=user, comment="comment", date="date")
            self.fail("invalid date allowed")
        except ValidationError:
            pass
