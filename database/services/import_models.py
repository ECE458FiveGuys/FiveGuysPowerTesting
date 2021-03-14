from datetime import timedelta

from database.exceptions import IllegalValueError
from database.models.model import Model
from database.services.import_service import ImportService


class ImportModels(ImportService):

    def __init__(self, file, min_column_enum, serializer):
        super(ImportModels, self).__init__(file, min_column_enum, serializer)

    def create_object(self, row):
        return Model.objects.create(
            vendor=self.parse_field(row, self.min_column_enum.VENDOR.value),
            model_number=self.parse_field(row, self.min_column_enum.MODEL_NUMBER.value),
            description=self.parse_field(row, self.min_column_enum.DESCRIPTION.value),
            comment=self.parse_field(row, self.min_column_enum.COMMENT.value),
            model_categories=self.parse_categories(row),
            calibration_frequency=self.parse_calibration_frequency(row),
            calibration_mode=self.parse_calibration_mode(row))

    def parse_categories(self, row):
        value = self.parse_field(row, self.min_column_enum.MODEL_CATEGORIES.value)
        return value.split()

    def parse_calibration_frequency(self, row):
        key = self.min_column_enum.CALIBRATION_FREQUENCY.value
        value = self.parse_field(row, key)
        if value == 'N/A':
            return timedelta(days=0)
        elif value.isdigit():
            return timedelta(days=int(value))
        else:
            raise IllegalValueError(self.reader.line_num, key, "positive integer", value)

    def parse_calibration_mode(self, row):
        key = self.min_column_enum.LOAD_BANK_SUPPORT.value
        value = self.parse_field(row, key)
        if value == 'Y':
            return 'LOAD_BANK'
        elif value == '':
            return 'DEFAULT'
        else:
            raise IllegalValueError(self.reader.line_num, key, "Y or empty string", value)
