from django.core.exceptions import ObjectDoesNotExist

from database.exceptions import IllegalAccessException, EntryDoesNotExistException
from database.services.deprecated.in_app_service import InAppService
from database.services.deprecated.instrument_services.select_instruments import SelectInstruments
from database.services.service import Service


class DeleteInstrument(InAppService):

    def __init__(
            self,
            user_id,
            password,
            instrument_id
    ):
        self.instrument_id = instrument_id
        super().__init__(user_id=user_id, password=password, admin_only=True)

    def execute(self):
        try:
            SelectInstruments(user_id=self.user.id, password=self.user.password, instrument_id=self.instrument_id)\
                .execute()\
                .get(id=self.instrument_id).delete()
        except ObjectDoesNotExist:
            raise EntryDoesNotExistException("instrument", self.instrument_id)
