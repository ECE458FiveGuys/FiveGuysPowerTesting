from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from database.exceptions import EntryDoesNotExistException
from database.models import Instrument, CalibrationEvent, User
from database.services.deprecated.in_app_service import InAppService
from database.services.deprecated.instrument_services.select_instruments import SelectInstruments
from database.services.deprecated.model_services import SelectModels
from database.services.deprecated.select_service import SelectService
from database.services.service import Service


class SelectCalibrationEvents(SelectService):

    def __init__(
            self,
            user_id,
            password,
            calibration_event_id=None,
            instrument_id=None,
            date=None,
            num_per_page=SelectService.ALL,
            order_by="date"
    ):
        self.calibration_event_id = calibration_event_id
        self.instrument_id = instrument_id
        self.date = date
        super().__init__(user_id=user_id, password=password, admin_only=False, num_per_page=num_per_page, order_by=order_by)

    def filter_by_fields(self):
        instrument = None
        if self.instrument_id is not None:
            try:
                instrument = SelectInstruments(user_id=self.user.id, password=self.user.password, instrument_id=self.instrument_id)\
                    .execute()\
                    .get(id=self.instrument_id)
            except ObjectDoesNotExist:
                raise EntryDoesNotExistException("instrument", self.instrument_id)

        query = None
        if self.calibration_event_id is not None:
            query = self.add_to_query(term=Q(id=self.calibration_event_id), query=query)
        if self.date is not None:
            query = self.add_to_query(term=Q(date=self.date), query=query)
        if instrument is not None:
            query = self.add_to_query(term=Q(instrument=instrument), query=query)

        if query is None:
            return CalibrationEvent.objects.all()
        else:
            return CalibrationEvent.objects.filter(query)

