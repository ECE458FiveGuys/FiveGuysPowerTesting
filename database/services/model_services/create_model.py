from django.db.utils import IntegrityError

from database.exceptions import IllegalAccessException, FieldCombinationNotUniqueException, RequiredFieldsEmptyException
from database.models import Model
from database.services.service import Service


class CreateModel(Service):

    def __init__(
            self,
            user,
            vendor,
            model_number,
            description,
            comment=None,
            calibration_frequency=None
    ):
        self.user = user
        self.vendor = vendor
        self.model_number = model_number
        self.description = description
        self.comment = comment
        self.calibration_frequency = calibration_frequency

    def execute(self):
        if not self.user.admin:
            raise IllegalAccessException()
        try:
            if Model.objects.filter(vendor=self.vendor, model_number=self.model_number).count() > 0:
                raise FieldCombinationNotUniqueException(object_type="model", fields_list=["vendor", "model_number"])
            Model.objects.create(vendor=self.vendor, model_number=self.model_number,
                                         description=self.description,
                                         comment=self.comment, calibration_frequency=self.calibration_frequency)
        except IntegrityError:
            raise RequiredFieldsEmptyException(object_type="model", required_fields_list=["vendor", "model_number"])
