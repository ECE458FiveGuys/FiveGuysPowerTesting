from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError

from database.exceptions import IllegalAccessException, FieldCombinationNotUniqueException, \
    RequiredFieldsEmptyException, EntryDoesNotExistException, InstrumentRequiredFieldsEmptyException, \
    InstrumentFieldCombinationNotUniqueException
from database.models import Instrument
from database.services.deprecated.in_app_service import InAppService
from database.services.deprecated.instrument_services.select_instruments import SelectInstruments
from database.services.deprecated.instrument_services.utils import handle_instrument_validation_error
from database.services.deprecated.model_services import SelectModels
from database.services.service import Service


class EditInstrument(InAppService):

    def __init__(
            self,
            user_id,
            password,
            instrument_id,
            model_id,
            serial_number,
            comment=None
    ):
        self.instrument_id = instrument_id
        self.model_id = model_id
        self.serial_number = serial_number
        self.comment = comment
        super().__init__(user_id=user_id, password=password, admin_only=True)

    def execute(self):
        if self.model_id is None:
            raise InstrumentRequiredFieldsEmptyException(None, None, self.serial_number)
        try:
            instrument = SelectInstruments(user_id=self.user.id, password=self.user.password,
                                           instrument_id=self.instrument_id) \
                .execute() \
                .get(id=self.instrument_id)
            try:
                model = SelectModels(user_id=self.user.id, password=self.user.password, model_id=self.model_id)\
                    .execute()\
                    .get(id=self.model_id)
                try:
                    if SelectInstruments(user_id=self.user.id, password=self.user.password, model_id=self.model_id,
                                         serial_number=self.serial_number)\
                            .execute()\
                            .exclude(id=self.instrument_id)\
                            .count() > 0:
                        raise InstrumentFieldCombinationNotUniqueException(
                            vendor=None if model is None else model.vendor,
                            model_number=None if model is None else model.model_number,
                            serial_number=self.serial_number)
                    instrument.model = model
                    instrument.serial_number = self.serial_number
                    instrument.comment = self.comment
                    instrument.full_clean()
                    instrument.save()
                    return instrument
                except ValidationError as e:
                    handle_instrument_validation_error(e,
                                                       None if model is None else model.vendor,
                                                       None if model is None else model.model_number,
                                                       self.serial_number)
            except ObjectDoesNotExist:
                raise EntryDoesNotExistException("model", self.model_id)
        except ObjectDoesNotExist:
           raise EntryDoesNotExistException("instrument", self.instrument_id)
