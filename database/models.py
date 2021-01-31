from django.db import models


class User(models.Model):
    username = models.TextField(blank=False, default=None)
    name = models.TextField(blank=False, default=None)
    email = models.EmailField(null=False, blank=False, default=None)
    password = models.TextField(blank=False, default=None)
    admin = models.BooleanField(blank=False, default=None)

    def __str__(self):
        return self.username, self.name, self.email, self.password, self.admin


class Model(models.Model):
    vendor = models.TextField(blank=False, default=None)
    model_number = models.TextField(blank=False, default=None)
    description = models.TextField(blank=False, default=None)
    comment = models.TextField(blank=True, null=True)
    calibration_frequency = models.IntegerField(blank=True, null=True)

    def is_calibratable(self):
        return self.calibration_frequency is not None

    def __str__(self):
        return self.vendor, self.model_number, self.description, self.comment, self.calibration_frequency


class Instrument(models.Model):
    model = models.ForeignKey(Model, on_delete=models.DO_NOTHING)
    serial_number = models.TextField(blank=False, default=None)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.model, self.serial_number, self.comment

    def is_calibratable(self):
        return self.model.is_calibratable()


class CalibrationEvent(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, blank=False, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.instrument, self.date, self.user, self.comment

