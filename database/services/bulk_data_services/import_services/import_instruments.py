from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from database.exceptions import InvalidCalibrationFrequencyException, DoesNotExistException, UserDoesNotExistException
from database.models import CalibrationEvent, Instrument, EquipmentModel
from database.serializers import EquipmentModelSerializer, InstrumentSerializer, InstrumentSerializerResponse
from database.services.bulk_data_services.import_service import ImportService
from database.services.bulk_data_services.table_enums import ModelTableColumnNames, InstrumentTableColumnNames
from user_portal.models import PowerUser


class ImportInstrumentsService(ImportService):

    def __init__(self, file):
        super().__init__(import_file=file, fields=[e.value for e in InstrumentTableColumnNames])

    def serialize(self, created_objects):
        return InstrumentSerializerResponse(created_objects, many=True)

    def create_object_from_row(self, row):
        vendor = self.parse_field(row, InstrumentTableColumnNames.VENDOR.value)
        model_number = self.parse_field(row, InstrumentTableColumnNames.MODEL_NUMBER.value)
        serial_number = self.parse_field(row, InstrumentTableColumnNames.SERIAL_NUMBER.value)
        instrument_comment = self.parse_field(row, InstrumentTableColumnNames.INSTRUMENT_COMMENT.value)
        calibration_username = self.parse_field(row, InstrumentTableColumnNames.CALIBRATION_USERNAME.value)
        calibration_date = self.parse_field(row, InstrumentTableColumnNames.CALIBRATION_DATE.value)
        calibration_comment = self.parse_field(row, InstrumentTableColumnNames.CALIBRATION_COMMENT.value)
        if calibration_username is None:
            calibration_username = 'admin'
        if calibration_date is not None:
            calibration_date = datetime.strptime(calibration_date, '%m/%d/%Y').date()
        try:
            user = PowerUser.objects.get(username=calibration_username)
            try:
                model = EquipmentModel.objects.get(vendor=vendor, model_number=model_number)

                instrument = Instrument.objects.create(model=model, serial_number=serial_number, comment=instrument_comment)
                CalibrationEvent.objects.create(instrument=instrument, user=user, date=calibration_date,
                                                                    comment=calibration_comment)
                return instrument
            except ObjectDoesNotExist:
                raise DoesNotExistException(vendor=vendor, model_number=model_number)
        except ObjectDoesNotExist:
            raise UserDoesNotExistException(user_name=calibration_username)