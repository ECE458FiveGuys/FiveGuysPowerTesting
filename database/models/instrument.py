from django.core.exceptions import ValidationError
from django.db import models

from database.constants import COMMENT_LENGTH, SERIAL_NUMBER_LENGTH
from database.exceptions import CHARACTER_LENGTH_ERROR_MESSAGE, InstrumentFieldLengthException, \
    InstrumentRequiredFieldsEmptyException, NULL_FIELD_ERROR_MESSAGE, UserError
from database.models.model import Model


class InstrumentManager(models.Manager):

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
                    raise InstrumentFieldLengthException("comment", COMMENT_LENGTH, model.vendor, model.model_number,
                                                         serial_number)
                else:
                    raise UserError(error_message)


class Instrument(models.Model):
    model = models.ForeignKey(Model, related_name='instruments', on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=SERIAL_NUMBER_LENGTH, blank=False)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, null=True)

    objects = InstrumentManager()

    class Meta:
        unique_together = ('model', 'serial_number')  # 2.2.1.2

    def __str__(self):
        template = '(Model:{0.model}, Serial Number:{0.serial_number}, Comment:{0.comment})'
        return template.format(self)

    def is_calibratable(self):
        return self.model.is_calibratable()
