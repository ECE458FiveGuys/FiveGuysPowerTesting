from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from database.exceptions import InvalidDateException
from database.exceptions import DoesNotExistException, ImpossibleCalibrationError, UserDoesNotExistException
from database.models.calibration_event import CalibrationEvent
from database.models.instrument import Instrument
from database.models.model import Model
from database.serializers.instrument import InstrumentSerializer
from database.services.bulk_data_services.import_service import ImportService
from database.services.bulk_data_services.table_enums import InstrumentTableColumnNames
from user_portal.models import PowerUser


class ImportInstrumentsService(ImportService):

    def __init__(self, file):
        super().__init__(import_file=file, fields=[e.value for e in InstrumentTableColumnNames])

    def serialize(self, created_objects):
        return InstrumentSerializer(created_objects, many=True)

    def create_objects_from_row(self, row):
        vendor = self.parse_field(row, InstrumentTableColumnNames.VENDOR.value)
        model_number = self.parse_field(row, InstrumentTableColumnNames.MODEL_NUMBER.value)
        serial_number = self.parse_field(row, InstrumentTableColumnNames.SERIAL_NUMBER.value)
        instrument_comment = self.parse_field(row, InstrumentTableColumnNames.INSTRUMENT_COMMENT.value)
        calibration_date = self.parse_field(row, InstrumentTableColumnNames.CALIBRATION_DATE.value)
        calibration_comment = self.parse_field(row, InstrumentTableColumnNames.CALIBRATION_COMMENT.value)
        try:
            user = PowerUser.objects.get(username='admin')
            try:
                model = Model.objects.get(vendor=vendor, model_number=model_number)

                if calibration_date is not None:
                    if model.calibration_frequency == timedelta(days=0):
                        raise ImpossibleCalibrationError(vendor=vendor,
                                                         model_number=model_number,
                                                         serial_number=serial_number)
                    try:
                        calibration_date = datetime.strptime(calibration_date, '%m/%d/%Y').date()
                        instrument = Instrument.objects.create(model=model, serial_number=serial_number,
                                                               comment=instrument_comment)
                        calibration_event = CalibrationEvent.objects.create(instrument=instrument,
                                                                            user=user,
                                                                            date=calibration_date,
                                                                            comment=calibration_comment)
                        return [instrument, calibration_event]  # type of first object returned is the type which will be serialized and returned
                    except ValueError:
                        raise InvalidDateException(calibration_date)
                instrument = Instrument.objects.create(model=model, serial_number=serial_number,
                                                       comment=instrument_comment)
                return [instrument]
            except ObjectDoesNotExist:
                raise DoesNotExistException(vendor=vendor, model_number=model_number)
        except ObjectDoesNotExist:
            raise UserDoesNotExistException(user_name='admin')
