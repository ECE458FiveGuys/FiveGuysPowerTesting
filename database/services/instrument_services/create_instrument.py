from database.exceptions import IllegalAccessException
from database.models import Instrument
from database.services.service import Service


class CreateInstrument(Service):

    def __init__(
            self,
            user,
            model_id,
            serial_number,
            comment=None
    ):
        self.user = user
        self.model_id = model_id
        self.serial_number = serial_number
        self.comment = comment

    def execute(self):
        if not self.user.admin:
            raise IllegalAccessException()
        try:
            Select
            if Instrument.objects.filter(vendor=self.vendor, model_number=self.model_number).count() > 0:
                raise FieldCombinationNotUniqueException(object_type="model", fields_list=["vendor", "model_number"])
            Model.objects.create(vendor=self.vendor, model_number=self.model_number,
                                         description=self.description,
                                         comment=self.comment, calibration_frequency=self.calibration_frequency)
        except IntegrityError:
            raise RequiredFieldsEmptyException(object_type="model", required_fields_list=["vendor", "model_number"])
