from django.db import models
from user_portal.models import PowerUser


class Model(models.Model):
    vendor = models.TextField(blank=False, default=None)
    model_number = models.TextField(blank=False, default=None)
    description = models.TextField(blank=False, default=None)
    comment = models.TextField(blank=True, null=True)
    calibration_frequency = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('vendor', 'model_number')  # 2.1.1.2

    def is_calibratable(self):
        return self.calibration_frequency is not None

    def __str__(self):
        return self.vendor, self.model_number, self.description, self.comment, self.calibration_frequency


class Instrument(models.Model):
    model = models.ForeignKey(Model, on_delete=models.DO_NOTHING)
    serial_number = models.TextField(blank=False, default=None)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('model', 'serial_number')  # 2.2.1.2

    def __str__(self):
        return self.model, self.serial_number, self.comment

    def is_calibratable(self):
        return self.model.is_calibratable()


class CalibrationEvent(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    date = models.DateField(null=False, blank=False, default=None)
    user = models.ForeignKey(PowerUser, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.instrument, self.date, self.user, self.comment
