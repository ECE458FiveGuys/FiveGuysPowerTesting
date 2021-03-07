import datetime
import random

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from database.constants import COMMENT_LENGTH, SERIAL_NUMBER_LENGTH
from database.exceptions import CHARACTER_LENGTH_ERROR_MESSAGE, CalibrationEventFieldLengthException, \
    CalibrationEventRequiredFieldsEmptyException, \
    INVALID_DATE_FIELD_ERROR_MESSAGE, InvalidDateException, NULL_FIELD_ERROR_MESSAGE, UserError
from database.models.instrument_category import InstrumentCategory
from database.models.model import Model
from user_portal.models import PowerUser as User


class InstrumentManager(models.Manager):

    def create(self,
               model=None,
               serial_number=None,
               comment=None,
               asset_tag_number=None):
        if asset_tag_number is None:
            used_values = self.asset_tag_numbers()
            asset_tag_number = random.choice(list(set(range(10 ** 5, 10 ** 6)) - set(used_values)))
        if comment is None:
            comment = ''
        instrument = Instrument(model=model,
                                serial_number=serial_number,
                                comment=comment,
                                asset_tag_number=asset_tag_number)
        instrument.full_clean()
        instrument.save()
        return instrument

    def create_for_import(self, vendor=None, model_number=None, serial_number=None, asset_tag_number=None, comment=None,
                          user=None, calibration_date=None, calibration_comment=None, instrument_categories=None):
        if vendor is None:
            raise ValidationError('Cannot import instrument without vendor')
        if model_number is None:
            raise ValidationError('Cannot import instrument without model number')
        if calibration_comment is None:
            calibration_comment = ''
        if instrument_categories is None:
            instrument_categories = []
        model = Model.objects.get(vendor=vendor, model_number=model_number)
        instrument = Instrument(model=model,
                                serial_number=serial_number,
                                comment=comment,
                                asset_tag_number=asset_tag_number)
        instrument.full_clean()
        instrument.save(using=self.db)
        for instrument_category in instrument_categories:
            ic, created = InstrumentCategory.objects.get_or_create(name=instrument_category)
            instrument.instrument_categories.add(ic)
        instrument.save()
        if calibration_date is not None:
            ce = CalibrationEvent.objects.create(user=user,
                                                 instrument=instrument,
                                                 date=calibration_date,
                                                 comment=calibration_comment)
            ce.full_clean()
            ce.save()
        return instrument

    def asset_tag_numbers(self):
        return self.order_by().values_list('asset_tag_number', flat=True)


class Instrument(models.Model):
    model = models.ForeignKey(Model, related_name='instruments', on_delete=models.PROTECT)
    serial_number = models.CharField(blank=True, null=True, max_length=SERIAL_NUMBER_LENGTH)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, default='')
    asset_tag_number = models.IntegerField(blank=True, unique=True,
                                           validators=[MinValueValidator(limit_value=100000),
                                                       MaxValueValidator(limit_value=999999)])
    instrument_categories = models.ManyToManyField(InstrumentCategory, related_name='instrument_list', blank=True)

    objects = InstrumentManager()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['model', 'serial_number'], name='unique_instrument')
        ]

    def __str__(self):
        template = '(Model:{0.model}, Serial Number:{0.serial_number}, Comment:{0.comment})'
        return template.format(self)

    def is_calibratable(self):
        return self.model.is_calibratable()


class CalibrationEventManager(models.Manager):

    def create(self,
               user=None,
               instrument=None,
               date=None,
               comment=None,
               additional_evidence=None,
               load_bank_data=None):
        if load_bank_data is None:
            load_bank_data = ''
        try:
            calibration_event = CalibrationEvent(instrument=instrument,
                                                 user=user,
                                                 date=date,
                                                 comment=comment,
                                                 additional_evidence=additional_evidence,
                                                 load_bank_data=load_bank_data)
            calibration_event.full_clean()
            calibration_event.save(using=self.db)
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


def instrument_evidence_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/instrument_<pk>/<filename>
    return 'instrument_{0}/{1}/{2}'.format(instance.instrument.pk, instance.date, filename)


class CalibrationEvent(models.Model):
    """
    Upload a file: The user may attach a single file of type JPG, PNG, GIF, PDF, or XLSX. Files larger than 32 MB must
    be rejected. Allowed for all models.
    """
    instrument = models.ForeignKey(Instrument, related_name='calibration_history', on_delete=models.CASCADE)
    date = models.DateField(blank=False, validators=[MaxValueValidator(limit_value=datetime.date.today)])
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, null=True)
    additional_evidence = models.FileField(upload_to=instrument_evidence_directory_path,
                                           blank=True,
                                           null=True,
                                           validators=[FileExtensionValidator(['jpg', 'png', 'gif', 'pdf', 'xlsx'])])
    load_bank_data = models.TextField(blank=True, default='')

    objects = CalibrationEventManager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        template = '(Instrument:{0.instrument}, Date:{0.date}, User:{0.user}, Comment:{0.comment})'
        return template.format(self)

    def clean(self):
        if not self.instrument.is_calibratable():
            raise ValidationError("Cannot add Calibration Event to Instrument whose Model cannot be calibrated")