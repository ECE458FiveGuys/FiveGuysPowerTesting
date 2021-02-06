import csv
import io
import zipfile

# from django.contrib.gis.geos import io
from django.conf.locale import cs
from django.test import TestCase

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
        decoded_response = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(decoded_response))
        print(next(reader))
