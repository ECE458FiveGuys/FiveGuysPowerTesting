import csv

from django.http import HttpResponse

from database.models import EquipmentModel
from database.services.bulk_data_services.export_service import ExportService
from database.services.bulk_data_services.table_enums import ModelTableColumnNames, ExportFileNames


class ExportModelsService(ExportService):
    def __init__(self):
        super().__init__(ExportFileNames.MODELS.value)

    def write_file(self, writer):
        models = EquipmentModel.objects.all()
        writer.writerow([e.value for e in ModelTableColumnNames])
        for model in models:
            writer.writerow([model.vendor,
                             model.model_number,
                             model.description,
                             model.comment,
                             "N/A" if model.calibration_frequency is None else model.calibration_frequency])
