from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from database.exceptions import IllegalAccessException, FieldCombinationNotUniqueException, \
    RequiredFieldsEmptyException, EntryDoesNotExistException
from database.models import Instrument, CalibrationEvent
from database.services.calibration_event_services.select_calibration_events import SelectCalibrationEvents
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.model_services.select_models import SelectModels
from database.services.service import Service


class CreateCalibrationEvent(Service):

    def __init__(
            self,
            user,
            instrument_id,
            date,
            comment=None
    ):
        self.instrument_id = instrument_id
        self.user = user
        self.date = date
        self.comment = comment

    def execute(self):
        try:
            instrument = SelectInstruments(instrument_id=self.instrument_id).execute().get(id=self.instrument_id)
            try:
                return CalibrationEvent.objects.create(instrument=instrument, user=self.user, date=self.date,
                                                       comment=self.comment)
            except IntegrityError:
                raise RequiredFieldsEmptyException(object_type="calibration event",
                                                   required_fields_list=["instrument id", "user", "date"])
        except ObjectDoesNotExist:
            raise EntryDoesNotExistException("instrument", self.instrument_id)
