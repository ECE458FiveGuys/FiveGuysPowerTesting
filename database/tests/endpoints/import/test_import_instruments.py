import csv
import tempfile
from datetime import timedelta

from rest_framework.test import force_authenticate

from database.exceptions import InvalidCalibrationFrequencyException
from database.models import EquipmentModel, Instrument, CalibrationEvent
from database.services.bulk_data_services.table_enums import ModelTableColumnNames, InstrumentTableColumnNames
from database.tests.endpoints.endpoint_test_case import EndpointTestCase
from database.tests.test_utils import create_model
from database.views import import_models, import_instruments


class ImportModelsTestCase(EndpointTestCase):

    def test_import_instrument_happy_case(self):
        model = create_model(1)
        response = self.make_import(endpoint=self.Endpoints.IMPORT_INSTRUMENTS.value,
                                    fields=[e.value for e in InstrumentTableColumnNames],
                                    row=[model.vendor,
                                         model.model_number,
                                         "serial_number",
                                         "comment",
                                         "1/12/2020",
                                         "comment"],
                                    function=import_instruments)
        if response.status_code != 200:
            self.fail("response failed with error: {}".format(response.content))
        instrument = Instrument.objects.get(serial_number="serial_number")
        calibration_event = CalibrationEvent.objects.get(instrument=instrument)
        if instrument.model.vendor != model.vendor \
            or instrument.model.model_number != model.model_number \
            or "serial_number" != instrument.serial_number \
            or "comment" != instrument.comment\
            or "2020-01-12" != calibration_event.date.__str__()\
            or "comment" != calibration_event.comment:
            self.fail("created model not found")


    def test_import_instrument_model_doesnt_exist(self):
        response = self.make_import(endpoint=self.Endpoints.IMPORT_INSTRUMENTS.value,
                                    fields=[e.value for e in InstrumentTableColumnNames],
                                    row=["vendor",
                                         "model_number",
                                         "serial_number",
                                         "comment",
                                         "1/12/2020",
                                         "comment"],
                                    function=import_instruments)
        if response.content.decode('utf-8') != "\"Error: The model with vendor 'vendor' and model number 'model_number' does not exist\"":
            self.fail("Instrument created with invalid model")
        if not self.none_of_model_exist(Instrument) or not self.none_of_model_exist(CalibrationEvent):
            self.fail("database not cleared of inputs after failed import")


    def test_import_instrument_with_calibration_date_but_no_frequency(self):
        model = create_model(calibration_freq=None)
        response = self.make_import(endpoint=self.Endpoints.IMPORT_INSTRUMENTS.value,
                                    fields=[e.value for e in InstrumentTableColumnNames],
                                    row=[model.vendor,
                                         model.model_number,
                                         "serial_number",
                                         "comment",
                                         "1/12/2020",
                                         "comment"],
                                    function=import_instruments)
        if response.content.decode('utf-8') != "\"Error: The instrument with vendor 'vendor', model number 'model_number', and serial number 'serial_number' has no calibration frequency but has a calibration date\"":
            self.fail("Instrument created with invalid model")
        if not self.none_of_model_exist(Instrument) or not self.none_of_model_exist(CalibrationEvent):
            self.fail("database not cleared of inputs after failed import")
