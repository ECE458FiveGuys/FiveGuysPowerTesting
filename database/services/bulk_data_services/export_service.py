import csv
import io

from django.http import HttpResponse

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from database.services.bulk_data_services.utils import VENDOR, MODEL_NUMBER, MODEL_DESCRIPTION, MODEL_COMMENT, \
    CALIBRATION_FREQUENCY
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
        workbook = Workbook()
        self.create_calibration_sheet(workbook)
        response = HttpResponse(save_virtual_workbook(workbook), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="calibration_events.csv"'
        return response

    def create_calibration_sheet(self, workbook):
        worksheet = workbook.create_sheet(title="Calibration Events")
        calibration_events = SelectCalibrationEvents(user_id=self.user.id, password=self.user.password, order_by="date")\
            .execute()
        worksheet.append([VENDOR, MODEL_NUMBER, MODEL_DESCRIPTION, MODEL_COMMENT, CALIBRATION_FREQUENCY])
        for calibration_event in calibration_events:
            worksheet.append([calibration_event.instrument.model.vendor,
                             calibration_event.instrument.model.model_number,
                             calibration_event.instrument.serial_number,
                             calibration_event.user.username,
                             calibration_event.date.__str__(),
                             calibration_event.comment])