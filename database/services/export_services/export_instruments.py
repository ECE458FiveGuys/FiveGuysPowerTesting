from database.services.bulk_data_services.export_service import ExportService
from database.services.export_services.export_utils import write_instrument_file
from database.services.table_enums import ExportFileNames


class ExportInstrumentsService(ExportService):

    def __init__(self):
        super().__init__(ExportFileNames.INSTRUMENTS.value)

    def write_file(self, writer, queryset):
        write_instrument_file(writer, queryset)
