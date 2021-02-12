import csv

from django.http import HttpResponse

from database.models import EquipmentModel, Instrument, CalibrationEvent
from database.services.bulk_data_services.export_service import ExportService
from database.services.bulk_data_services.table_enums import ModelTableColumnNames, InstrumentTableColumnNames, ExportFileNames


class ExportInstrumentsService(ExportService):

    def __init__(self):
        super().__init__(ExportFileNames.INSTRUMENTS.value)

    def write_file(self, writer):
        instruments = Instrument.objects.all()
        writer.writerow([e.value for e in InstrumentTableColumnNames])
        for instrument in instruments:
            latest_calibration_event = CalibrationEvent.objects \
                .filter(instrument=instrument) \
                .order_by("date") \
                .first()
            writer.writerow([instrument.model.vendor,
                             instrument.model.model_number,
                             instrument.serial_number,
                             instrument.comment,
                             None if latest_calibration_event is None else latest_calibration_event.date,
                             None if latest_calibration_event is None else latest_calibration_event.comment])
