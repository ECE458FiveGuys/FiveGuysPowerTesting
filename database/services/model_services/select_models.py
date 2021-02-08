from django.db.models import Q

from database.models import Model
from database.services.in_app_service import InAppService
from database.services.select_service import SelectService
from database.services.service import Service


class SelectModels(SelectService):

    def __init__(
            self,
            user_id,
            password,
            model_id=None,
            vendor=None,
            model_number=None,
            description=None,
            calibration_frequency=None,
            num_per_page=SelectService.ALL,
            order_by=None
    ):
        self.id = model_id
        self.vendor = vendor
        self.model_number = model_number
        self.description = description
        self.calibration_frequency = calibration_frequency
        super().__init__(user_id=user_id, password=password, admin_only=False, num_per_page=num_per_page, order_by=order_by)

    def filter_by_fields(self):
        query = None
        if self.id is not None:
            query = self.add_to_query(term=Q(id=self.id), query=query)
        if self.vendor is not None:
            query = self.add_to_query(term=Q(vendor=self.vendor), query=query)
        if self.model_number is not None:
            query = self.add_to_query(term=Q(model_number=self.model_number), query=query)
        if self.description is not None:
            query = self.add_to_query(term=Q(description=self.description), query=query)
        if self.calibration_frequency is not None:
            query = self.add_to_query(term=Q(calibration_frequency=self.calibration_frequency), query=query)

        if query is None:
            return Model.objects.all()
        else:
            return Model.objects.filter(query)



