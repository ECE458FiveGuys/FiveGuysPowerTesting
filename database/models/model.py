from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models

from database.constants import COMMENT_LENGTH, DESCRIPTION_LENGTH, MODEL_NUMBER_LENGTH, VENDOR_LENGTH
from database.exceptions import CHARACTER_LENGTH_ERROR_MESSAGE, ModelFieldLengthException, \
    ModelRequiredFieldsEmptyException, NULL_FIELD_ERROR_MESSAGE, UserError
from database.models.model_category import ModelCategory


class ModelManager(models.Manager):

    def create(self,
               vendor=None,
               model_number=None,
               description=None,
               comment='',
               calibration_frequency=timedelta(days=0),
               calibration_mode='FILE'):
        try:
            if calibration_frequency is None:
                calibration_frequency = timedelta(days=0)
            m = Model(vendor=vendor,
                      model_number=model_number,
                      description=description,
                      comment=comment,
                      calibration_frequency=calibration_frequency,
                      calibration_mode=calibration_mode)
            m.full_clean()
            m.save()
            return m
        except ValidationError as e:
            for error_message in e.messages:
                if NULL_FIELD_ERROR_MESSAGE in error_message:
                    raise ModelRequiredFieldsEmptyException(vendor=vendor, model_number=model_number)
                elif CHARACTER_LENGTH_ERROR_MESSAGE.format(VENDOR_LENGTH) in error_message:
                    raise ModelFieldLengthException("vendor", VENDOR_LENGTH, vendor, model_number)
                elif CHARACTER_LENGTH_ERROR_MESSAGE.format(MODEL_NUMBER_LENGTH) in error_message:
                    raise ModelFieldLengthException("model number", MODEL_NUMBER_LENGTH, vendor, model_number)
                elif CHARACTER_LENGTH_ERROR_MESSAGE.format(DESCRIPTION_LENGTH) in error_message:
                    raise ModelFieldLengthException("description", DESCRIPTION_LENGTH, vendor, model_number)
                elif CHARACTER_LENGTH_ERROR_MESSAGE.format(COMMENT_LENGTH) in error_message:
                    raise ModelFieldLengthException("comment", COMMENT_LENGTH, vendor, model_number)
                else:
                    raise UserError(error_message)


class Model(models.Model):
    CALIBRATION_CHOICES = [
        ('SIMPLE', 'Simple Event with Comment'),
        ('FILE', 'Simple Event or File Input'),
        ('ALL', 'All Modes of Calibration')
    ]

    vendor = models.CharField(blank=False, max_length=VENDOR_LENGTH)
    model_number = models.CharField(blank=False, max_length=MODEL_NUMBER_LENGTH)
    description = models.CharField(blank=False, max_length=DESCRIPTION_LENGTH)
    comment = models.CharField(blank=True, default='', max_length=COMMENT_LENGTH)
    calibration_frequency = models.DurationField(blank=True, default=timedelta(days=0))
    model_categories = models.ManyToManyField(ModelCategory, related_name='model_list', blank=True)
    calibration_mode = models.CharField(blank=True, max_length=6, choices=CALIBRATION_CHOICES, default='FILE')

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
