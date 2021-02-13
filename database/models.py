from datetime import date

from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.core.validators import MaxValueValidator

from database.exceptions import NULL_FIELD_ERROR_MESSAGE, ModelRequiredFieldsEmptyException, \
    CHARACTER_LENGTH_ERROR_MESSAGE, ModelFieldLengthException, UserError, InstrumentRequiredFieldsEmptyException, \
    InstrumentFieldLengthException, CalibrationEventRequiredFieldsEmptyException, CalibrationEventFieldLengthException, \
    INVALID_DATE_FIELD_ERROR_MESSAGE, InvalidDateException
from user_portal.models import PowerUser as User

VENDOR_LENGTH = 30
MODEL_NUMBER_LENGTH = 40
SERIAL_NUMBER_LENGTH = 40
DESCRIPTION_LENGTH = 100
COMMENT_LENGTH = 2000
CALIBRATION_FREQUENCY_LENGTH = 10  # needs to be validated in manager, length not valid for integer field


class EquipmentModelManager(models.Manager):

    def create(self,
               vendor=None,
               model_number=None,
               description=None,
               comment=None,
               calibration_frequency=None):
        try:
            model = EquipmentModel(vendor=vendor, model_number=model_number,
                                   description=description,
                                   comment=comment,
                                   calibration_frequency=calibration_frequency)
            model.full_clean()
            model.save()
            return model
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


class InstrumentModelManager(models.Manager):

    def create(self,
               model=None,
               serial_number=None,
               comment=None):
        try:
            instrument = Instrument(model=model, serial_number=serial_number, comment=comment)
            instrument.full_clean()
            instrument.save()
            return instrument
        except ValidationError as e:
            for error_message in e.messages:
                if NULL_FIELD_ERROR_MESSAGE in error_message:
                    raise InstrumentRequiredFieldsEmptyException(None if model is None else model.vendor,
                                                                 None if model is None else model.model_number,
                                                                 serial_number)
                elif CHARACTER_LENGTH_ERROR_MESSAGE.format(SERIAL_NUMBER_LENGTH) in error_message:
                    raise InstrumentFieldLengthException("serial number", SERIAL_NUMBER_LENGTH, model.vendor,
                                                         model.model_number,
                                                         serial_number)
                elif CHARACTER_LENGTH_ERROR_MESSAGE.format(COMMENT_LENGTH) in error_message:
                    raise InstrumentFieldLengthException("commment", COMMENT_LENGTH, model.vendor, model.model_number,
                                                         serial_number)
                else:
                    raise UserError(error_message)


class CalibrationEventManager(models.Manager):

    def create(self,
               user=None,
               instrument=None,
               date=None,
               comment=None):
        try:
            calibration_event = CalibrationEvent(instrument=instrument, user=user, date=date,
                                                 comment=comment)
            calibration_event.full_clean()
            calibration_event.save()
            return calibration_event
        except ValidationError as e:
            for error_message in e.messages:
                if NULL_FIELD_ERROR_MESSAGE in error_message:
                    raise CalibrationEventRequiredFieldsEmptyException(vendor=None if instrument is None or instrument.model is None else instrument.model.vendor,
                                                                       model_number=None if instrument is None or instrument.model is None else instrument.model.model_number,
                                                                       serial_number=None if instrument is None or instrument.model is None else instrument.model.serial_number,
                                                                       date=date)
                elif CHARACTER_LENGTH_ERROR_MESSAGE.format(COMMENT_LENGTH) in error_message:
                    raise CalibrationEventFieldLengthException("commment", COMMENT_LENGTH,
                                                               vendor=None if instrument is None or instrument.model is None else instrument.model.vendor,
                                                               model_number=None if instrument is None or instrument.model is None else instrument.model.model_number,
                                                               serial_number=None if instrument is None else instrument.serial_number,
                                                               date=date)
                elif INVALID_DATE_FIELD_ERROR_MESSAGE in error_message:
                    raise InvalidDateException()
                else:
                    raise UserError(error_message)


class EquipmentModel(models.Model):
    vendor = models.CharField(blank=False, null=False, max_length=VENDOR_LENGTH)
    model_number = models.CharField(blank=False, null=False, max_length=MODEL_NUMBER_LENGTH)
    description = models.CharField(blank=False, null=False, max_length=DESCRIPTION_LENGTH)
    comment = models.CharField(blank=True, null=True, max_length=COMMENT_LENGTH)
    calibration_frequency = models.IntegerField(blank=True, null=True)

    objects = EquipmentModelManager()

    class Meta:
        unique_together = ('vendor', 'model_number')  # 2.1.1.2

    def is_calibratable(self):
        return self.calibration_frequency is not None

    def __str__(self):
        template = '(Vendor:{0.vendor}, Model Number:{0.model_number}, Description:{0.description}, Comment:{' \
                   '0.comment}, Calibration Frequency:{0.calibration_frequency})'
        return template.format(self)


class Instrument(models.Model):
    model = models.ForeignKey(EquipmentModel, related_name='instruments', on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=SERIAL_NUMBER_LENGTH, blank=False)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, null=True)

    objects = InstrumentModelManager()

    class Meta:
        unique_together = ('model', 'serial_number')  # 2.2.1.2
        ordering = ['model__vendor', 'model__model_number']

    def __str__(self):
        template = '(Model:{0.model}, Serial Number:{0.serial_number}, Comment:{0.comment})'
        return template.format(self)

    def is_calibratable(self):
        return self.model.is_calibratable()


class CalibrationEvent(models.Model):
    instrument = models.ForeignKey(Instrument, related_name='calibration_history', on_delete=models.CASCADE)
    date = models.DateField(blank=False, validators=[MaxValueValidator(limit_value=date.today)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, null=True)

    objects = CalibrationEventManager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        template = '(Instrument:{0.instrument}, Date:{0.date}, User:{0.user}, Comment:{0.comment})'
        return template.format(self)
