import sys

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError

from database.exceptions import IllegalAccessException, RequiredFieldsEmptyException, \
    FieldCombinationNotUniqueException, EntryDoesNotExistException, ModelFieldCombinationNotUniqueException
from database.models import Model
from database.services.in_app_service import InAppService
from database.services.model_services.select_models import SelectModels
from database.services.model_services.utils import handle_model_validation_error
from database.services.service import Service
from database.services.utils.constants import NOT_APPLICABLE


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
            model = SelectModels(user_id=self.user.id, password=self.user.password, model_id=self.id) \
                .execute() \
                .get(id=self.id)
            model.vendor = self.vendor
            model.model_number = self.model_number
            model.description = self.description
            model.comment = self.comment,
            model.calibration_frequency = None if self.calibration_frequency is NOT_APPLICABLE else self.calibration_frequency
            if Model.objects.filter(vendor=self.vendor, model_number=self.model_number).exclude(id=self.id):
                raise ModelFieldCombinationNotUniqueException(self.vendor, self.model_number)
            try:
                model.full_clean()
                model.save()
                return model
            except ValidationError as e:
                handle_model_validation_error(e, vendor=self.vendor, model_number=self.model_number)
        except ObjectDoesNotExist:
            raise EntryDoesNotExistException("model", self.id)
