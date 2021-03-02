from datetime import timedelta

from database.exceptions import InvalidCalibrationFrequencyException
from database.models.model import Model
from database.serializers.model import ModelSerializer
from database.services.bulk_data_services.import_service import ImportService
from database.services.bulk_data_services.table_enums import ModelTableColumnNames


class ImportModelsService(ImportService):

    def __init__(self, file):
        super().__init__(import_file=file, fields=[e.value for e in ModelTableColumnNames])

    def serialize(self, created_objects):
        return ModelSerializer(created_objects, many=True)

    def create_objects_from_row(self, row):
        vendor = self.parse_field(row, ModelTableColumnNames.VENDOR.value)
        model_number = self.parse_field(row, ModelTableColumnNames.MODEL_NUMBER.value)
        description = self.parse_field(row, ModelTableColumnNames.DESCRIPTION.value)
        comment = self.parse_field(row, ModelTableColumnNames.COMMENT.value)
        calibration_frequency = None if row[ModelTableColumnNames.CALIBRATION_FREQUENCY.value] == 'N/A' \
            else row[ModelTableColumnNames.CALIBRATION_FREQUENCY.value]
        if calibration_frequency is not None:
            try:
                calibration_frequency = timedelta(days=int(calibration_frequency))
                if calibration_frequency <= timedelta(days=0):
                    raise InvalidCalibrationFrequencyException(vendor, model_number)
            except (SyntaxError, ValueError):
                raise InvalidCalibrationFrequencyException(vendor, model_number)
        model = Model.objects.create(vendor=vendor,
                                     model_number=model_number,
                                     description=description,
                                     comment=comment,
                                     calibration_frequency=calibration_frequency)

        return [model]
