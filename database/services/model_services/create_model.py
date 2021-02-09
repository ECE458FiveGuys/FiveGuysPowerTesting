from django.db.utils import IntegrityError

from database.exceptions import IllegalAccessException, FieldCombinationNotUniqueException, \
    RequiredFieldsEmptyException, InactiveUserException
from database.models import EquipmentModel, User
from database.services.in_app_service import InAppService
from database.services.service import Service


class CreateModel(InAppService):

    def __init__(
            self,
            user_id,
            password,
            vendor,
            model_number,
            description,
            comment=None,
            calibration_frequency=None
    ):
        self.vendor = vendor
        self.model_number = model_number
        self.description = description
        self.comment = comment
        self.calibration_frequency = calibration_frequency
        super().__init__(user_id=user_id, password=password, admin_only=True)

    def execute(self):
        try:
            if EquipmentModel.objects.filter(vendor=self.vendor, model_number=self.model_number).count() > 0:
                raise FieldCombinationNotUniqueException(object_type="model", fields_list=["vendor", "model_number"])
            return EquipmentModel.objects.create(vendor=self.vendor, model_number=self.model_number,
                                                 description=self.description,
                                                 comment=self.comment, calibration_frequency=self.calibration_frequency)
        except IntegrityError:
            raise RequiredFieldsEmptyException(object_type="model", required_fields_list=["vendor", "model_number"])
