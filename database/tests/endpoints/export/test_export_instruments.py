# import csv
# import io
# import tempfile
#
# from rest_framework.test import force_authenticate
#
# from database.services.table_enums import InstrumentTableColumnNames
# from database.tests.endpoints.endpoint_test_case import EndpointTestCase
# from database.tests.test_utils import create_calibration_events
# from database.views import export_instruments
#
#
# class CreateInstrumentsTestCase(EndpointTestCase):
#
#     def test_export_models_happy_case(self):
#         calibration_event, calibration_event2, calibration_event3, user, model, instrument = create_calibration_events()
#         request = self.factory.get(self.Endpoints.EXPORT_INSTRUMENTS.value)
#         force_authenticate(request, self.admin)
#         response = export_instruments(request)
#         if response.status_code != 200:
#             self.fail("instruments could not be exported")
#         self.assertEquals(
#             response.get('Content-Disposition'),
#             'attachment; filename=instruments.csv'
#         )
#         new_file = tempfile.TemporaryFile()
#         new_file.write(response.content)
#         new_file.seek(0)
#         param_file = io.TextIOWrapper(new_file)
#         reader = csv.DictReader(param_file)
#         if set(reader.fieldnames) != set([e.value for e in InstrumentTableColumnNames]):
#             self.fail("field names not correct")
#         list_of_dict = list(reader)
#         row = list_of_dict[0]
#         if row[InstrumentTableColumnNames.VENDOR.value] != model.vendor \
#                 or row[InstrumentTableColumnNames.MODEL_NUMBER.value] != model.model_number \
#                 or row[InstrumentTableColumnNames.COMMENT.value] != "" \
#                 or row[InstrumentTableColumnNames.SERIAL_NUMBER.value] != instrument.serial_number \
#                 or row[InstrumentTableColumnNames.CALIBRATION_DATE.value] != "{}/{}/{}".format(
#             calibration_event3.date.month,
#             calibration_event3.date.day,
#             calibration_event3.date.year):
#             self.fail("created instrument not found")
