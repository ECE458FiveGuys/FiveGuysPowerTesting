import csv
import io

from django.http import HttpResponse

from openpyxl import Workbook

from database.services.calibration_event_services.select_calibration_events import SelectCalibrationEvents
from database.services.in_app_service import InAppService
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.model_services.select_models import SelectModels


class Export(InAppService):
    def __init__(
            self,
            user_id,
            password,
    ):
        super().__init__(user_id=user_id, password=password, admin_only=True)

    def execute(self):
        # response = HttpResponse(content_type='application/force-download')
        # response['Content-Disposition'] = 'attachment; filename="calibration_events.csv"'
        # writer = csv.writer(response)
        # calibration_events = SelectCalibrationEvents(user_id=self.user.id, password=self.user.password, order_by="date")\
        #     .execute()
        # for calibration_event in calibration_events:
        #     writer.writerow([calibration_event.instrument.model.vendor,
        #                      calibration_event.instrument.model.model_number,
        #                      calibration_event.instrument.serial_number,
        #                      calibration_event.user.username,
        #                      calibration_event.date,
        #                      calibration_event.comment])
        output = io.BytesIO()
        wb = Workbook()
        self.create_calibration_sheet(workbook)
        workbook.close()
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="calibration_events.csv"'
        return response

    def create_calibration_sheet(self, workbook):
        worksheet = workbook.add_worksheet()
        calibration_events = SelectCalibrationEvents(user_id=self.user.id, password=self.user.password, order_by="date")\
            .execute()
        row = 0
        for calibration_event in calibration_events:
            worksheet.write_row(row, 0, [calibration_event.instrument.model.vendor,
                             calibration_event.instrument.model.model_number,
                             calibration_event.instrument.serial_number,
                             calibration_event.user.username,
                             calibration_event.date,
                             calibration_event.comment])
            row+=1