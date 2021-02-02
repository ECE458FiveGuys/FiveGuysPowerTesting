from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from database.exceptions import EntryDoesNotExistException
from database.models import Instrument, CalibrationEvent, User
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.model_services.select_models import SelectModels
from database.services.service import Service


class SelectCalibrationEvents(Service):

    def __init__(
            self,
            calibration_event_id=None,
            user=None,
            instrument_id=None,
            date=None,
            chronological=True
    ):
        self.calibration_event_id = calibration_event_id
        self.instrument_id = instrument_id
        self.user = user
        self.date = date
        self.chronological = chronological

    def execute(self):
        calibration_events = CalibrationEvent.objects.all()

        # filter by instrument fields

        calibration_events = calibration_events if self.calibration_event_id is None else calibration_events.filter(
            id=self.calibration_event_id)
        calibration_events = calibration_events if self.date is None else calibration_events.filter(date=self.date)
        calibration_events = calibration_events if self.user is None else calibration_events.filter(user=self.user)

        instrument = None
        if self.instrument_id is not None:
            try:
                instrument = SelectInstruments(instrument_id=self.instrument_id).execute().get(id=self.instrument_id)
            except ObjectDoesNotExist:
                raise EntryDoesNotExistException("instrument", self.instrument_id)

        calibration_events = calibration_events if instrument is None else calibration_events.filter(user=instrument)

        if self.chronological:
            calibration_events = calibration_events.order_by("-date")

        return calibration_events
