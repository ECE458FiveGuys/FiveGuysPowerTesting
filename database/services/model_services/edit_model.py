from django.db import IntegrityError

from database.exceptions import IllegalAccessException, RequiredFieldsEmptyException, \
    FieldCombinationNotUniqueException, EntryDoesNotExistException
from database.models import Model
from database.services.service import Service


class EditModel(Service):

    def __init__(
            self,
            user,
            model_id,
            vendor,
            model_number,
            description,
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
        if not self.user.admin:
            raise IllegalAccessException()
        try:
            if not Model.objects.filter(id=self.id):
                raise EntryDoesNotExistException("model", self.id)
            if Model.objects.filter(vendor=self.vendor, model_number=self.model_number).exclude(id=self.id):
                raise FieldCombinationNotUniqueException(object_type="model", fields_list=["vendor", "model_number"])
            model = Model(id=self.id, vendor=self.vendor, model_number=self.model_number,
                                         description=self.description,
                                         comment=self.comment, calibration_frequency=self.calibration_frequency)
            model.save()
            return model
        except IntegrityError:
            raise RequiredFieldsEmptyException(object_type="model", required_fields_list=["vendor", "model_number"])
