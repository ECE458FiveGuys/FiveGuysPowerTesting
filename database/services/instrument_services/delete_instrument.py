from django.core.exceptions import ObjectDoesNotExist

from database.exceptions import IllegalAccessException, EntryDoesNotExistException
from database.services.instrument_services.select_instruments import SelectInstruments
from database.services.service import Service


class DeleteInstrument(Service):

    def __init__(
            self,
            user,
            instrument_id
    ):
        self.user = user
        self.instrument_id = instrument_id

    def execute(self):
        if not self.user.admin:
            raise IllegalAccessException()
        try:
            SelectInstruments(instrument_id=self.instrument_id).execute().get(id=self.instrument_id).delete()
        except ObjectDoesNotExist:
            raise EntryDoesNotExistException("instrument", self.instrument_id)
