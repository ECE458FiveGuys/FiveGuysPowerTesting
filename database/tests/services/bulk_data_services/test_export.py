import csv
import io
import tempfile
import zipfile

# from django.contrib.gis.geos import io
from django.conf.locale import cs
from django.test import TestCase
from openpyxl import load_workbook

from database.services.bulk_data_services.export_service import Export
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
        print([sheet["A2"].value, sheet["B2"].value, sheet["C2"].value, sheet["D2"].value, sheet["E2"].value])
        new_file.close()
        # decoded_response = response.content.decode('utf-8')
        # reader = csv.reader(io.StringIO(decoded_response))
        # print(next(reader))
        #decoded_response = response.content.decode('utf-8')
        print(sheet)
        #print(next(reader))

