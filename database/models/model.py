from datetime import timedelta

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from database.constants import COMMENT_LENGTH, DESCRIPTION_LENGTH, MODEL_NUMBER_LENGTH, VENDOR_LENGTH
from database.models.model_category import ModelCategory


class ModelManager(models.Manager):

    def create(self,
               vendor=None,
               model_number=None,
               description=None,
               comment=None,
               calibration_frequency=None,
               model_categories=None,
               calibration_mode=None):
        if comment is None:
            comment = ''
        if calibration_frequency is None or calibration_frequency == timedelta(days=0):
            calibration_frequency = timedelta(days=0)
            calibration_mode = 'NOT_CALIBRATABLE'
        if model_categories is None:
            model_categories = []
        if calibration_mode is None:
            calibration_mode = 'DEFAULT'

        m = Model(vendor=vendor,
                  model_number=model_number,
                  description=description,
                  comment=comment,
                  calibration_frequency=calibration_frequency,
                  calibration_mode=calibration_mode)
        m.full_clean()
        m.save(using=self.db)
        for model_category in model_categories:
            mc, created = ModelCategory.objects.get_or_create(name=model_category)
            m.model_categories.add(mc)
        m.save()
        return m

    def vendors(self, model_number):
        if model_number is None:
            model_number = ''
        return self.order_by().filter(model_number__contains=model_number).values_list('vendor', flat=True).distinct()

    def model_numbers(self, vendor):
        if vendor is None:
            vendor = ''
        return self.order_by().filter(vendor__contains=vendor).values_list('model_number', flat=True).distinct()


class Model(models.Model):
    CALIBRATION_CHOICES = [
        ('NOT_CALIBRATABLE', 'Cannot calibrate this instrument'),
        ('DEFAULT', 'Simple Event or File Input'),
        ('LOAD_BANK', 'Simple Event, File Input, or Load Bank Input')
    ]

    vendor = models.CharField(blank=False, max_length=VENDOR_LENGTH)
    model_number = models.CharField(blank=False, max_length=MODEL_NUMBER_LENGTH)
    description = models.CharField(blank=False, max_length=DESCRIPTION_LENGTH)
    comment = models.CharField(blank=True, default='', max_length=COMMENT_LENGTH)
    calibration_frequency = models.DurationField(blank=True,
                                                 default=timedelta(days=0),
                                                 validators=[MinValueValidator(timedelta(days=0)),
                                                             MaxValueValidator(timedelta(days=3653))])
    model_categories = models.ManyToManyField(ModelCategory, related_name='model_list', blank=True)
    calibration_mode = models.CharField(blank=True, max_length=16, choices=CALIBRATION_CHOICES, default='DEFAULT')

    objects = ModelManager()

    class Meta:
        unique_together = ('vendor', 'model_number')
        ordering = ['vendor', 'model_number']

    def is_calibratable(self):
        return self.calibration_frequency is not None

    def __str__(self):
        template = '(Vendor:{0.vendor}, Model Number:{0.model_number}, Description:{0.description}, Comment:{' \
                   '0.comment}, Calibration Frequency:{0.calibration_frequency}, Calibration Mode:{0.calibration_mode})'
        return template.format(self)
