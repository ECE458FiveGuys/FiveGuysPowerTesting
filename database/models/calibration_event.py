from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models

from database.constants import COMMENT_LENGTH
from database.exceptions import CHARACTER_LENGTH_ERROR_MESSAGE, CalibrationEventFieldLengthException, \
    CalibrationEventRequiredFieldsEmptyException, INVALID_DATE_FIELD_ERROR_MESSAGE, \
    InvalidDateException, NULL_FIELD_ERROR_MESSAGE, UserError
from database.models.instrument import Instrument
from user_portal.models import PowerUser as User


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
                    raise CalibrationEventRequiredFieldsEmptyException(
                        vendor=None if instrument is None or instrument.model is None else instrument.model.vendor,
                        model_number=None if instrument is None or instrument.model is None else instrument.model.model_number,
                        serial_number=None if instrument is None or instrument.model is None else instrument.model.serial_number,
                        date=date)
                elif CHARACTER_LENGTH_ERROR_MESSAGE.format(COMMENT_LENGTH) in error_message:
                    raise CalibrationEventFieldLengthException("comment", COMMENT_LENGTH,
                                                               vendor=None if instrument is None or instrument.model is None else instrument.model.vendor,
                                                               model_number=None if instrument is None or instrument.model is None else instrument.model.model_number,
                                                               serial_number=None if instrument is None else instrument.serial_number,
                                                               date=date)
                elif INVALID_DATE_FIELD_ERROR_MESSAGE in error_message:
                    raise InvalidDateException(date)
                else:
                    raise UserError(error_message)


class CalibrationEvent(models.Model):
    instrument = models.ForeignKey(Instrument, related_name='calibration_history', on_delete=models.CASCADE)
    date = models.DateField(blank=False, validators=[MaxValueValidator(limit_value=date.today)])
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, null=True)

    objects = CalibrationEventManager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        template = '(Instrument:{0.instrument}, Date:{0.date}, User:{0.user}, Comment:{0.comment})'
        return template.format(self)

    def clean(self):
        if not self.instrument.is_calibratable():
            raise ValidationError("Cannot add Calibration Event to Instrument whose Model that cannot be calibrated")
