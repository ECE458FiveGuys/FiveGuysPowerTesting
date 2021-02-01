from django.db.models import Q

from database.models import Instrument
from database.services.model_services.select_models import SelectModels
from database.services.service import Service


class SelectInstruments(Service):

    def __init__(
            self,
            instrument_id=None,
            model_id=None,
            model_number=None,
            vendor=None,
            description=None,
            serial_number=None
    ):
        self.instrument_id = instrument_id
        self.model_id = model_id
        self.model_number = model_number
        self.vendor = vendor
        self.description = description
        self.serial_number = serial_number

    def execute(self):
        instruments = Instrument.objects.all()

        # filter by instrument fields

        instruments = instruments if self.instrument_id is None else instruments.filter(id=self.instrument_id)
        instruments = instruments if self.serial_number is None else instruments.filter(
            serial_number=self.serial_number)

        # filter by model fields

        models = SelectModels(model_id=self.model_id, model_number=self.model_number, vendor=self.vendor,
                              description=self.description).execute()
        query = None
        for model in models:
            if query is None:
                query = Q(model_id=model.id)
            else:
                query.add(Q(model_id=model.id), Q.OR)
        instruments = instruments if query is None else instruments.filter(query)

        return instruments
