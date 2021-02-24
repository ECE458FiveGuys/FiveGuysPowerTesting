import random

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import DateField, ExpressionWrapper, F, Max

from database.constants import COMMENT_LENGTH, SERIAL_NUMBER_LENGTH
from database.exceptions import CHARACTER_LENGTH_ERROR_MESSAGE, InstrumentFieldLengthException, \
    InstrumentRequiredFieldsEmptyException, NULL_FIELD_ERROR_MESSAGE, UserError
from database.models.instrument_category import InstrumentCategory
from database.models.model import Model


class InstrumentManager(models.Manager):
    def get_queryset(self):
        mrc = Max('calibration_history__date')
        cf = F('model__calibration_frequency')
        expiration = ExpressionWrapper(mrc + cf, output_field=DateField())
        qs = super().get_queryset().annotate(most_recent_calibration_date=mrc)
        return qs.annotate(calibration_expiration_date=expiration)

    def create(self,
               model=None,
               serial_number=None,
               comment='',
               asset_tag_number=None):
        if asset_tag_number is None:
            used_values = self.asset_tag_numbers()
            asset_tag_number = random.choice(list(set(range(10 ** 5, 10 ** 6)) - set(used_values)))
        if comment is None:
            comment = ''
        try:
            instrument = Instrument(model=model,
                                    serial_number=serial_number,
                                    comment=comment,
                                    asset_tag_number=asset_tag_number)
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

    def asset_tag_numbers(self):
        return self.order_by().values_list('asset_tag_number', flat=True)


class Instrument(models.Model):
    model = models.ForeignKey(Model, related_name='instruments', on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=SERIAL_NUMBER_LENGTH)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, default='')
    asset_tag_number = models.IntegerField(blank=True, unique=True,
                                           validators=[MinValueValidator(limit_value=100000),
                                                       MaxValueValidator(limit_value=999999)])
    instrument_categories = models.ManyToManyField(InstrumentCategory, related_name='instrument_list', blank=True)

    objects = InstrumentManager()

    class Meta:
        unique_together = ('model', 'serial_number')  # 2.2.1.2

    def __str__(self):
        template = '(Model:{0.model}, Serial Number:{0.serial_number}, Comment:{0.comment})'
        return template.format(self)

    def is_calibratable(self):
        return self.model.is_calibratable()
