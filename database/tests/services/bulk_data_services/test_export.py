import csv
import io
import tempfile
import zipfile

# from django.contrib.gis.geos import io
from django.conf.locale import cs
from django.test import TestCase
from django.utils.timezone import localtime, now
from openpyxl import load_workbook

from database.services.bulk_data_services.export_service import Export
from database.services.bulk_data_services.table_enums import ModelTableColumnNames, InstrumentTableColumnNames, \
    CalibrationEventColumnNames, SheetNames

from database.tests.services.service_test_utils import create_calibration_events, create_admin, create_3_instruments


class ExportTestCase(TestCase):
    def test_export_happy_case(self):
        calibration_event, calibration_event2, calibration_event3, user, model, instrument = create_calibration_events()
        create_3_instruments(model, instrument)
        admin = create_admin()
        response = Export(user_id=admin.id, password=admin.password).execute()
        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename="calibration_events.csv"'
        )
        new_file = tempfile.TemporaryFile()
        new_file.write(response.content)
        wb = load_workbook(new_file)
        self.validate_calibration_events_sheet(wb)
        self.validate_instruments_sheet(wb)
        self.validate_models_sheet(wb)
        new_file.close()

    def validate_calibration_events_sheet(self, workbook):
        sheet = workbook.get_sheet_by_name(SheetNames.CALIBRATION_EVENTS.value)
        date = localtime(now()).date()
        date2 = localtime(now()).date().replace(month=date.month + 1)
        date3 = localtime(now()).date().replace(month=date2.month + 1)
        self.assertEquals(
            set([sheet["A1"].value, sheet["B1"].value, sheet["C1"].value, sheet["D1"].value, sheet["E1"].value, sheet["F1"].value]),
            set([ModelTableColumnNames.VENDOR.value,
                 ModelTableColumnNames.MODEL_NUMBER.value,
                 InstrumentTableColumnNames.SERIAL_NUMBER.value,
                 CalibrationEventColumnNames.CALIBRATION_USERNAME.value,
                 CalibrationEventColumnNames.CALIBRATION_DATE.value,
                 CalibrationEventColumnNames.CALIBRATION_COMMENT.value])
        )
        self.assertEquals(
            set([sheet["A2"].value, sheet["B2"].value, sheet["C2"].value, sheet["D2"].value, sheet["E2"].value]),
            set(['vendor', 'model_number', 'serial_number', 'username2', date.__str__()])
        )
        self.assertEquals(
            set([sheet["A3"].value, sheet["B3"].value, sheet["C3"].value, sheet["D3"].value, sheet["E3"].value]),
            set(['vendor', 'model_number', 'serial_number', 'username2', date2.__str__()])
        )
        self.assertEquals(
            set([sheet["A4"].value, sheet["B4"].value, sheet["C4"].value, sheet["D4"].value, sheet["E4"].value]),
            set(['vendor', 'model_number', 'serial_number', 'username2', date3.__str__()])
        )

    def validate_instruments_sheet(self, workbook):
        sheet = workbook.get_sheet_by_name(SheetNames.INSTRUMENTS.value)
        self.assertEquals(
            set([sheet["A1"].value, sheet["B1"].value, sheet["C1"].value, sheet["D1"].value]),
            set([ModelTableColumnNames.VENDOR.value,
                          ModelTableColumnNames.MODEL_NUMBER.value,
                          InstrumentTableColumnNames.SERIAL_NUMBER.value,
                          InstrumentTableColumnNames.INSTRUMENT_COMMENT.value])
        )
        self.assertEquals(
            set([sheet["A2"].value, sheet["B2"].value, sheet["C2"].value, sheet["D2"].value]),
            set(['vendor', 'model_number', 'serial_number', 'comment'])
        )
        self.assertEquals(
            set([sheet["A3"].value, sheet["B3"].value, sheet["C3"].value, sheet["D3"].value]),
            set(['vendor', 'model_number', 'serial_number2', None])
        )
        self.assertEquals(
            set([sheet["A4"].value, sheet["B4"].value, sheet["C4"].value, sheet["D4"].value]),
            set(['vendor2', 'model_number2', 'serial_number2', None])
        )

    def validate_models_sheet(self, workbook):
        sheet = workbook.get_sheet_by_name(SheetNames.MODELS.value)
        self.assertEquals(
            set([sheet["A1"].value, sheet["B1"].value, sheet["C1"].value, sheet["D1"].value, sheet["E1"].value]),
            set([ModelTableColumnNames.VENDOR.value,
                          ModelTableColumnNames.MODEL_NUMBER.value,
                          ModelTableColumnNames.MODEL_DESCRIPTION.value,
                          ModelTableColumnNames.MODEL_COMMENT.value,
                          ModelTableColumnNames.CALIBRATION_FREQUENCY.value])
        )
        self.assertEquals(
            set([sheet["A2"].value, sheet["B2"].value, sheet["C2"].value, sheet["D2"].value, sheet["E2"].value]),
            set(['vendor', 'model_number', 'description', 'comment', 1])
        )
        self.assertEquals(
            set([sheet["A3"].value, sheet["B3"].value, sheet["C3"].value, sheet["D3"].value, sheet["E3"].value]),
            set(['vendor2', 'model_number2', 'description2', 'comment2', 2])
        )