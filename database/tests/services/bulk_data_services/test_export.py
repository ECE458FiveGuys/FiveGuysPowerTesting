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
from database.services.bulk_data_services.utils import VENDOR, MODEL_NUMBER, MODEL_DESCRIPTION, MODEL_COMMENT, \
    CALIBRATION_FREQUENCY
from database.tests.services.service_test_utils import create_calibration_events, create_admin


class ExportTestCase(TestCase):
    def test_export_happy_case(self):
        calibration_event, calibration_event2, calibration_event3, user = create_calibration_events()
        admin = create_admin()
        response = Export(user_id=admin.id, password=admin.password).execute()
        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename="calibration_events.csv"'
        )
        new_file = tempfile.TemporaryFile()
        new_file.write(response.content)
        wb = load_workbook(new_file)
        sheet = wb.get_sheet_by_name("Calibration Events")
        date = localtime(now()).date()
        date2 = localtime(now()).date().replace(month=date.month + 1)
        date3 = localtime(now()).date().replace(month=date2.month + 1)
        self.assertEquals(
                set([sheet["A1"].value, sheet["B1"].value, sheet["C1"].value, sheet["D1"].value, sheet["E1"].value]),
                set([VENDOR, MODEL_NUMBER, MODEL_DESCRIPTION, MODEL_COMMENT, CALIBRATION_FREQUENCY])
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
        new_file.close()

