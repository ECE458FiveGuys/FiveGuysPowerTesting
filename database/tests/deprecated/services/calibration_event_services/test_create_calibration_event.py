# from django.test import TestCase
#
# from database.exceptions import IllegalAccessException, EntryDoesNotExistException, RequiredFieldsEmptyException, \
#     FieldLengthException, InvalidDateException
# from database.models import User
# from database.services.calibration_event_services.create_calibration_event import CreateCalibrationEvent
# from database.services.calibration_event_services.select_calibration_events import SelectCalibrationEvents
# from database.services.instrument_services.create_instrument import CreateInstrument
# from database.tests.services.service_test_utils import create_admin_and_model, create_admin_and_model_and_instrument, \
#     OVERLONG_STRING
# from django.utils.timezone import localtime, now
#
# class CreateCalibrationEventTestCase(TestCase):
#     def test_create_instrument_happy_case(self):
#         user, model, instrument = create_admin_and_model_and_instrument()
#         calib_event = CreateCalibrationEvent(user_id=user.id, password="password", instrument_id=instrument.id, date=localtime(now()).date())\
#             .execute()
#         calib_events = SelectCalibrationEvents(user_id=user.id, password="password").execute()
#         if calib_events.count() != 1 or calib_events.get(id=calib_event.id) != calib_event:
#             self.fail("selected wrong instrument")
#
#
#     def test_create_instrument_invalid_instrument_id_exception(self):
#         user, model, instrument = create_admin_and_model_and_instrument()
#         try:
#             CreateCalibrationEvent(user_id=user.id, password="password", instrument_id=instrument.id + 1,
#                                                  date=localtime(now()).date()) \
#                 .execute()
#             self.fail("calibration event with invalid instrument_id allowed to be created")
#         except EntryDoesNotExistException as e:
#             expected_message = "The instrument with id {} no longer exists".format(instrument.id + 1)
#             if e.message == expected_message:
#                 pass
#             else:
#                 self.fail("Incorrect error message.\n Actual: {} \n Expected: {}".format(e.message, expected_message))
#
#
#     def test_create_instrument_without_required_fields_throws_exception(self):
#         user, model, instrument = create_admin_and_model_and_instrument()
#         try:
#             CreateCalibrationEvent(user_id=user.id, password="password", instrument_id=None, date=None) \
#                 .execute()
#             self.fail("calibration event without required fields was created")
#         except RequiredFieldsEmptyException as e:
#             if e.message != "instrument id and user and date are required fields for calibration event":
#                 message = "incorrect error message thrown: {}".format(e.message)
#                 self.fail(message)
#             pass
#
#     # Field validity tests
#
#     def test_overlong_comment_field_test(self):
#         user, model, instrument = create_admin_and_model_and_instrument()
#         try:
#             CreateCalibrationEvent(instrument_id=instrument.id, user_id=user.id, password=user.password, comment=OVERLONG_STRING, date=localtime(now()).date()).execute()
#             self.fail("overlong comment allowed")
#         except FieldLengthException:
#             pass
#
#     def test_invalid_date_field_test(self):
#         user, model, instrument = create_admin_and_model_and_instrument()
#         try:
#             CreateCalibrationEvent(instrument_id=instrument.id, user_id=user.id, password=user.password, comment="comment", date="date").execute()
#             self.fail("invalid date allowed")
#         except InvalidDateException:
#             pass