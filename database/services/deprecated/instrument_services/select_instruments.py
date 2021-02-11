from django.db.models import Q

from database.models import Instrument
from database.services.deprecated.in_app_service import InAppService
from database.services.deprecated.model_services import SelectModels
from database.services.deprecated.select_service import SelectService
from database.services.service import Service


class SelectInstruments(SelectService):

    def __init__(
            self,
            user_id,
            password,
            instrument_id=None,
            model_id=None,
            model_number=None,
            vendor=None,
            description=None,
            serial_number=None,
            num_per_page=SelectService.ALL,
            order_by=None
    ):
        self.instrument_id = instrument_id
        self.model_id = model_id
        self.model_number = model_number
        self.vendor = vendor
        self.description = description
        self.serial_number = serial_number
        super().__init__(user_id=user_id, password=password, admin_only=False, num_per_page=num_per_page,
                         order_by=order_by)

    def filter_by_fields(self):
        # build filter for model fields

        models = SelectModels(user_id=self.user.id, password=self.user.password, model_id=self.model_id,
                              model_number=self.model_number, vendor=self.vendor,
                              description=self.description).execute()

        model_field_query = None
        for model in models:
            model_field_query = self.add_to_query(term=Q(model=model), query=model_field_query, operation=Q.OR)

        main_query = None
        if self.instrument_id is not None:
            main_query = self.add_to_query(term=Q(id=self.instrument_id), query=main_query)
        if self.serial_number is not None:
            main_query = self.add_to_query(term=Q(serial_number=self.serial_number), query=main_query)

        if main_query is None and model_field_query is None:
            return Instrument.objects.all()
        elif main_query is None:
            return Instrument.objects.filter(model_field_query)
        elif model_field_query is None:
            return Instrument.objects.filter(main_query)
        else:
            return Instrument.objects.filter(main_query) & \
                   Instrument.objects.filter(model_field_query)
