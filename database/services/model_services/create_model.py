from django.core.exceptions import ValidationError


from database.exceptions import FieldCombinationNotUniqueException
from database.models import EquipmentModel

from database.services.in_app_service import InAppService
from database.services.model_services.utils import handle_model_validation_error
from database.services.utils.constants import NOT_APPLICABLE


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
            model = EquipmentModel(vendor=self.vendor, model_number=self.model_number,
                                   description=self.description,
                                   comment=self.comment,
                                   calibration_frequency=None if self.calibration_frequency is NOT_APPLICABLE else self.calibration_frequency)
            model.full_clean()
            model.save()
            return model
        except ValidationError as e:
            handle_model_validation_error(e, self.vendor, self.model_number)
