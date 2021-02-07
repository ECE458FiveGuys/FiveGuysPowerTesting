from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from database.exceptions import IllegalAccessException, FieldCombinationNotUniqueException, \
    RequiredFieldsEmptyException, InactiveUserException, UserError, FieldLengthException, \
    CHARACTER_LENGTH_ERROR_MESSAGE, NULL_FIELD_ERROR_MESSAGE, ModelFieldCombinationNotUniqueException
from database.models import Model, User, VENDOR_LENGTH, MODEL_NUMBER_LENGTH, DESCRIPTION_LENGTH, COMMENT_LENGTH
from database.services.in_app_service import InAppService
from database.services.model_services.utils import handle_model_validation_error
from database.services.service import Service
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
            if Model.objects.filter(vendor=self.vendor, model_number=self.model_number).count() > 0:
                raise ModelFieldCombinationNotUniqueException(self.vendor, self.model_number)
            model = Model(vendor=self.vendor, model_number=self.model_number,
                                         description=self.description,
                                         comment=self.comment,
                                        calibration_frequency=None if self.calibration_frequency is NOT_APPLICABLE else self.calibration_frequency)
            model.full_clean()
            model.save()
            return model
        except ValidationError as e:
            handle_model_validation_error(e, self.vendor, self.model_number)
