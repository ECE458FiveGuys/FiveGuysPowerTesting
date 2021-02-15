from database.services.bulk_data_services.export_service import ExportService
from database.services.bulk_data_services.export_services.export_utils import write_model_file
from database.services.bulk_data_services.table_enums import ExportFileNames


class ExportModelsService(ExportService):
    def __init__(self):
        super().__init__(ExportFileNames.MODELS.value)

    def write_file(self, writer):
        write_model_file(writer)