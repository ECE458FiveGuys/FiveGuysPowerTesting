from django.db import models
from user_portal.models import PowerUser as User

VENDOR_LENGTH = 30
MODEL_NUMBER_LENGTH = 40
SERIAL_NUMBER_LENGTH = 40
DESCRIPTION_LENGTH = 100
COMMENT_LENGTH = 200


class EquipmentModel(models.Model):
    vendor = models.TextField(blank=False)
    model_number = models.TextField(blank=False)
    description = models.TextField(blank=False)
    comment = models.TextField(blank=True)
    calibration_frequency = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('vendor', 'model_number')  # 2.1.1.2

    def is_calibratable(self):
        return self.calibration_frequency is not None

    def __str__(self):
        return self.vendor, self.model_number, self.description, self.comment, self.calibration_frequency


class Instrument(models.Model):
    model = models.ForeignKey(EquipmentModel, related_name='instruments', on_delete=models.DO_NOTHING)
    serial_number = models.CharField(max_length=SERIAL_NUMBER_LENGTH, blank=False)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, null=True)

    class Meta:
        unique_together = ('model', 'serial_number')  # 2.2.1.2

    def __str__(self):
        return self.model, self.serial_number, self.comment

    def is_calibratable(self):
        return self.model.is_calibratable()


class CalibrationEvent(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    date = models.DateField(blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.instrument, self.date, self.user, self.comment

