from django.db import IntegrityError

from database.exceptions import IllegalAccessException, RequiredFieldsEmptyException, FieldCombinationNotUniqueException
from database.models import Model


class EditModel:

    def __init__(
            self,
            user,
            model_id,
            vendor,
            model_number,
            description=None,
            comment=None,
            calibration_frequency=None,
    ):
        self.user = user
        self.id = model_id
        self.vendor = vendor
        self.model_number = model_number
        self.description = description
        self.comment = comment
        self.calibration_frequency = calibration_frequency

    def execute(self):
        if not self.user.is_admin():
            raise IllegalAccessException()
        try:
            model = Model.objects.create(id=self.id, vendor=self.vendor, model_number=self.model_number,
                                         description=self.description,
                                         comment=self.comment, calibration_frequency=self.calibration_frequency)
            if Model.objects.filter(vendor=self.vendor, model_number=self.model_number).exclude(id=self.id):
                raise FieldCombinationNotUniqueException(object_type="model", fields_list=["vendor", "model_number"])
            model.save()
        except IntegrityError:
            raise RequiredFieldsEmptyException(object_type="model", required_fields_list=["vendor", "model_number"])
