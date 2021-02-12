from rest_framework.request import Request

from database.exceptions import InvalidCalibrationFrequencyException
from database.models import EquipmentModel
from database.serializers import EquipmentModelSerializer
from database.services.bulk_data_services.import_service import ImportService
from database.services.bulk_data_services.table_enums import ModelTableColumnNames


class ImportModelsService(ImportService):

    def __init__(self, file):
        super().__init__(import_file=file, fields=[e.value for e in ModelTableColumnNames])

    def serialize(self, created_objects):
        return EquipmentModelSerializer(created_objects, many=True)

    def create_objects_from_row(self, row):
        vendor = self.parse_field(row, ModelTableColumnNames.VENDOR.value)
        model_number = self.parse_field(row, ModelTableColumnNames.MODEL_NUMBER.value)
        description = self.parse_field(row, ModelTableColumnNames.MODEL_DESCRIPTION.value)
        comment = self.parse_field(row, ModelTableColumnNames.MODEL_COMMENT.value)
        calibration_frequency = None if row[ModelTableColumnNames.CALIBRATION_FREQUENCY.value] == 'N/A' \
            else row[ModelTableColumnNames.CALIBRATION_FREQUENCY.value]
        if calibration_frequency is not None:
            try:
                calibration_frequency = int(calibration_frequency)
                if calibration_frequency <= 0:
                    raise InvalidCalibrationFrequencyException(vendor, model_number)
            except (SyntaxError, ValueError):
                raise InvalidCalibrationFrequencyException(vendor, model_number)
        model = EquipmentModel.objects.create(vendor=vendor,
                                              model_number=model_number,
                                              description=description,
                                              comment=comment,
                                              calibration_frequency=calibration_frequency)

        return [model]
