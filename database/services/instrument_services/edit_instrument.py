from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from database.exceptions import IllegalAccessException, FieldCombinationNotUniqueException, \
    RequiredFieldsEmptyException, EntryDoesNotExistException
from database.models import Instrument
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.model_services.select_models import SelectModels
from database.services.service import Service


class EditInstrument(Service):

    def __init__(
            self,
            user,
            instrument_id,
            model_id,
            serial_number,
            comment=None
    ):
        self.user = user
        self.instrument_id = instrument_id
        self.model_id = model_id
        self.serial_number = serial_number
        self.comment = comment

    def execute(self):
        if not self.user.admin:
            raise IllegalAccessException()
        if self.model_id is None:
            raise RequiredFieldsEmptyException(object_type="instrument",
                                               required_fields_list=["model", "serial_number"])
        if not Instrument.objects.filter(id=self.instrument_id):
            raise EntryDoesNotExistException("instrument", self.instrument_id)
        try:
            model = SelectModels(model_id=self.model_id).execute().get(id=self.model_id)
            try:
                if SelectInstruments(model_id=self.model_id, serial_number=self.serial_number).execute().exclude(id=self.instrument_id).count() > 0:
                    raise FieldCombinationNotUniqueException(object_type="instrument", fields_list=["model", "serial_number"])
                instrument = Instrument(id=self.instrument_id, model=model, serial_number=self.serial_number,
                                             comment=self.comment)
                instrument.save()
                return instrument
            except IntegrityError:
                raise RequiredFieldsEmptyException(object_type="instrument", required_fields_list=["model", "serial_number"])
        except ObjectDoesNotExist:
            raise EntryDoesNotExistException("model", self.model_id)