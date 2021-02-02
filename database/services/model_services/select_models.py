from database.models import Model
from database.services.service import Service


class SelectModels(Service):

    def __init__(
            self,
            model_id=None,
            vendor=None,
            model_number=None,
            description=None,
            calibration_frequency=None,
            num_per_page=None,
            page_num=None
    ):
        self.id = model_id
        self.vendor = vendor
        self.model_number = model_number
        self.description = description
        self.calibration_frequency = calibration_frequency

    def execute(self):
        models = Model.objects.all()
        models = models if self.id is None else models.filter(id=self.id)
        models = models if self.vendor is None else models.filter(vendor=self.vendor)
        models = models if self.model_number is None else models.filter(model_number=self.model_number)
        models = models if self.description is None else models.filter(description=self.description)
        models = models if self.calibration_frequency is None else models.filter(calibration_frequency=self.calibration_frequency)
        return models



