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


class CreateInstrument(InAppService):

    def __init__(
            self,
            user_id,
            password,
            model_id,
            serial_number,
            comment=None
    ):
        self.model_id = model_id
        self.serial_number = serial_number
        self.comment = comment
        super().__init__(user_id=user_id, password=password, admin_only=True)

    def execute(self):
        if self.model_id is None:
            raise InstrumentRequiredFieldsEmptyException(None, None, self.serial_number)
        try:
            model = SelectModels(user_id=self.user.id, password=self.user.password, model_id=self.model_id)\
                .execute()\
                .get(id=self.model_id)
            try:
                if SelectInstruments(user_id=self.user.id, password=self.user.password, model_id=self.model_id, serial_number=self.serial_number)\
                        .execute()\
                        .count() > 0:
                    raise InstrumentFieldCombinationNotUniqueException(
                                                   vendor=model.vendor,
                                                   model_number=model.model_number,
                                                   serial_number=self.serial_number)
                instrument = Instrument(model=model, serial_number=self.serial_number,
                                             comment=self.comment)
                instrument.full_clean()
                instrument.save()
                return instrument
            except ValidationError as e:
                handle_instrument_validation_error(e,
                                                   vendor=model.vendor,
                                                   model_number=model.model_number,
                                                   serial_number=self.serial_number)
        except ObjectDoesNotExist:
            raise EntryDoesNotExistException("model", self.model_id)
