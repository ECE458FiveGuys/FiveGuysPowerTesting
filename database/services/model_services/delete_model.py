from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from database.exceptions import IllegalAccessException, EntryDoesNotExistException, UserError
from database.models import Model
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.model_services.select_models import SelectModels
from database.services.service import Service


class DeleteModel(Service):

    def __init__(
            self,
            user,
            model_id
    ):
        self.user = user
        self.model_id = model_id

    def execute(self):
        if not self.user.admin:
            raise IllegalAccessException()
        if SelectInstruments(instrument_id=self.model_id).execute().count() > 0:
            raise UserError("Cannot be deleted, as instruments of this model exist")
        try:
            SelectModels(model_id=self.model_id).execute().get(id=self.model_id).delete()
        except ObjectDoesNotExist:
            raise EntryDoesNotExistException("model", self.model_id)
