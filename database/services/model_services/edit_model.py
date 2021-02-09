from django.db import IntegrityError

from database.exceptions import IllegalAccessException, RequiredFieldsEmptyException, \
    FieldCombinationNotUniqueException, EntryDoesNotExistException
from database.models import EquipmentModel
from database.services.in_app_service import InAppService
from database.services.service import Service


class EditModel(InAppService):

    def __init__(
            self,
            user_id,
            password,
            model_id,
            vendor,
            model_number,
            description,
            comment=None,
            calibration_frequency=None,
    ):
        self.id = model_id
        self.vendor = vendor
        self.model_number = model_number
        self.description = description
        self.comment = comment
        self.calibration_frequency = calibration_frequency
        super().__init__(user_id=user_id, password=password, admin_only=True)

    def execute(self):
        try:
            if not EquipmentModel.objects.filter(id=self.id):
                raise EntryDoesNotExistException("model", self.id)
            if EquipmentModel.objects.filter(vendor=self.vendor, model_number=self.model_number).exclude(id=self.id):
                raise FieldCombinationNotUniqueException(object_type="model", fields_list=["vendor", "model_number"])
            model = EquipmentModel(id=self.id, vendor=self.vendor, model_number=self.model_number,
                                   description=self.description,
                                   comment=self.comment, calibration_frequency=self.calibration_frequency)
            model.save()
            return model
        except IntegrityError:
            raise RequiredFieldsEmptyException(object_type="model", required_fields_list=["vendor", "model_number"])
