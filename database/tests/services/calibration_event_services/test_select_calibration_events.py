from datetime import datetime, time

from django.test import TestCase

from database.models import EquipmentModel, Instrument, CalibrationEvent
from database.services.calibration_event_services.select_calibration_events import SelectCalibrationEvents
from database.services.instrument_services.select_instruments import SelectInstruments
from database.tests.services.service_test_utils import create_non_admin_user
from django.utils.timezone import localtime, now

class SelectCalibrationEventsTestCase(TestCase):

    def test_select_all_calibration_events_happy_case(self):
        calibration_event, calibration_event2, calibration_event3, user = self.create_calibration_events()
        calib_events = SelectCalibrationEvents(user_id=user.id, password=user.password).execute()
        if calib_events.count() != 3:
            self.fail("selected wrong calibration events")

    def test_select_all_calibration_events_chronological(self):
        calibration_event, calibration_event2, calibration_event3, user = self.create_calibration_events()
        calib_events = SelectCalibrationEvents(user_id=user.id, password=user.password, order_by="date").execute()
        if calib_events.count() != 3 or calib_events.first() != calibration_event:
            self.fail("selected wrong calibration events")

    def test_select_calib_events_by_calib_event_id(self):
        calibration_event, calibration_event2, calibration_event3, user = self.create_calibration_events()
        calib_events = SelectCalibrationEvents(user_id=user.id, password=user.password, calibration_event_id=calibration_event.id).execute()
        if calib_events.count() != 1 or calib_events.get(id=calibration_event.id) != calibration_event:
            self.fail("selected wrong calibration event")

    def test_select_calib_events_by_instrument_id(self):
        calibration_event, calibration_event2, calibration_event3, user = self.create_calibration_events()
        calib_events = SelectCalibrationEvents(user_id=user.id, password=user.password, instrument_id=calibration_event.instrument.id).execute()
        if calib_events.count() != 3 or \
                calib_events.get(id=calibration_event.id) != calibration_event or \
                calib_events.get(id=calibration_event2.id) != calibration_event2 or \
                calib_events.get(id=calibration_event3.id) != calibration_event3:
            self.fail("selected wrong calibration_event")

    def test_select_calib_events_by_date(self):
        calibration_event, calibration_event2, calibration_event3, user = self.create_calibration_events()
        calib_events = SelectCalibrationEvents(user_id=user.id, password=user.password, date=calibration_event.date).execute()
        if calib_events.count() != 1 or calib_events.get(date=calibration_event.date) != calibration_event:
            self.fail("selected wrong calibration event")

    def test_select_calib_events_by_multiple_fields(self):
        calibration_event, calibration_event2, calibration_event3, user = self.create_calibration_events()
        calib_events = SelectCalibrationEvents(user_id=user.id, password=user.password, date=calibration_event.date, calibration_event_id=calibration_event2.instrument.id).execute()
        if calib_events.count() != 0:
            self.fail("selected wrong calibration event")

        calib_events = SelectCalibrationEvents(user_id=user.id, password=user.password, date=calibration_event.date, instrument_id=calibration_event.instrument.id).execute()
        if calib_events.count() != 1 or calib_events.get(date=calibration_event.date) != calibration_event:
            self.fail("selected wrong calibration event")



    def create_calibration_events(self):
        user = create_non_admin_user()
        model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description",
                                              comment="comment", calibration_frequency=1)
        instrument = Instrument.objects.create(model=model, serial_number="serial_number")
        earlier = localtime(now()).date()
        later = localtime(now()).date().replace(month=earlier.month + 1)
        latest = localtime(now()).date().replace(month=earlier.month + 2)
        calibration_event3 = CalibrationEvent.objects.create(instrument=instrument, user=user, date=latest)
        calibration_event = CalibrationEvent.objects.create(instrument=instrument, user=user, date=earlier)
        calibration_event2 = CalibrationEvent.objects.create(instrument=instrument, user=user, date=later)
        return calibration_event, calibration_event2, calibration_event3, user
