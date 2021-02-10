from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from database.exceptions import IllegalAccessException, EntryDoesNotExistException, UserError
from database.models import EquipmentModel
from database.services.in_app_service import InAppService
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.model_services.select_models import SelectModels
from database.services.service import Service


class DeleteModel(InAppService):

    def __init__(
            self,
            user_id,
            password,
            model_id
    ):
        self.model_id = model_id
        super().__init__(user_id=user_id, password=password, admin_only=True)

    def execute(self):
        if SelectInstruments(user_id=self.user.id, password=self.user.password, instrument_id=self.model_id).execute().count() > 0:
            raise UserError("Cannot be deleted, as instruments of this model exist")
        try:
            SelectModels(user_id=self.user.id, password=self.user.password, model_id=self.model_id).execute().get(id=self.model_id).delete()
        except ObjectDoesNotExist:
            raise EntryDoesNotExistException("model", self.model_id)
