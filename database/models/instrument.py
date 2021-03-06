import random
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import DateField, ExpressionWrapper, F, OuterRef, Subquery, UniqueConstraint

from database.constants import CALIBRATION_EVENT_TEMPLATE, COMMENT_LENGTH, INSTRUMENT_TEMPLATE, SERIAL_NUMBER_LENGTH
from database.models.instrument_category import InstrumentCategory
from database.models.model import Model
from database.validators import validate_max_date
from user_portal.models import User as User


class InstrumentManager(models.Manager):

    def create(
            self,
            model=None,
            serial_number=None,
            comment=None,
            asset_tag_number=None
    ):
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

    def create_for_import(
            self,
            vendor=None,
            model_number=None,
            serial_number=None,
            asset_tag_number=None,
            comment=None,
            user=None,
            calibration_date=None,
            calibration_comment=None,
            instrument_categories=None
    ):
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
            if created:
                ic.full_clean()
            instrument.instrument_categories.add(ic)
        instrument.save()
        if calibration_date is not None:
            ce = CalibrationEvent.objects.create_for_import(
                user=user,
                instrument=instrument,
                date=calibration_date,
                comment=calibration_comment
            )
            ce.full_clean()
            ce.save()
        return instrument

    def asset_tag_numbers(self, pks=None):
        if pks is None:
            return self.order_by().values_list('asset_tag_number', flat=True)
        else:
            return self.order_by().filter(pk__in=pks).values_list('asset_tag_number', flat=True)

    def calibratable_asset_tag_numbers(self):
        return self.order_by().exclude(model__calibration_mode='NOT_CALIBRATABLE').values_list('asset_tag_number', flat=True)

    def can_calibrate(self, instrument, calibrator):
        """ Returns False if calibrating instrument with calibrator would result in a cycle. """
        queue = [(calibrator, datetime.today().astimezone())]  # initial queue

        while queue:
            n, date = queue.pop(0)
            calibration_event = CalibrationEvent.objects.find_calibration_event(n.pk, date)
            if calibration_event is not None:
                if instrument in calibration_event.calibrated_with.all():
                    return False

                queue.extend([(i, calibration_event.date) for i in calibration_event.calibrated_with.all()])

        return True

    def calibrators(self, instrument):
        sq = CalibrationEvent.objects.filter(instrument=OuterRef('pk')).filter(approval_data__approved=True)
        expression = F('most_recent_calibration_date') + F('model__calibration_frequency')
        expiration = ExpressionWrapper(expression, output_field=DateField())
        qs = self.order_by('pk').exclude(pk=instrument.pk)\
            .filter(model__model_categories__in=instrument.model.calibrator_categories.all())\
            .annotate(most_recent_calibration_date=Subquery(sq.order_by('-date').values('date')[:1]))\
            .annotate(calibration_expiration_date=expiration)\
            .filter(calibration_expiration_date__gte=datetime.today().astimezone())
        calibrators = []
        for calibrator in qs:
            if self.can_calibrate(instrument, calibrator):
                calibrators.append(calibrator.pk)

        return qs.filter(pk__in=calibrators)


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
        return INSTRUMENT_TEMPLATE.format(self)

    def is_calibratable(self):
        return self.model.is_calibratable()


class CalibrationEventManager(models.Manager):

    def create(
            self,
            user=None,
            instrument=None,
            date=None,
            comment=None,
            additional_evidence=None,
            load_bank_data=None,
            guided_hardware_data=None,
            custom_data=None,
            calibrated_with=None,
    ):
        if comment is None:
            comment = ''
        if load_bank_data is None:
            load_bank_data = ''
        if guided_hardware_data is None:
            guided_hardware_data = ''
        if custom_data is None:
            custom_data = ''
        if calibrated_with is None:
            calibrated_with = []

        calibration_event = CalibrationEvent(
            instrument=instrument,
            user=user,
            date=date,
            comment=comment,
            additional_evidence=additional_evidence,
            load_bank_data=load_bank_data,
            guided_hardware_data=guided_hardware_data,
            custom_data=custom_data,
        )
        calibration_event.full_clean()
        calibration_event.save(using=self.db)

        if not instrument.model.approval_required:
            approval_data = ApprovalData(
                calibration_event=calibration_event,
                approved=True,
                approver=user,
                date=datetime.utcnow().astimezone(),
                comment='',
            )
            approval_data.save(using=self.db)
            calibration_event.approval_data = approval_data
            calibration_event.save(using=self.db)

        for instrument in calibrated_with:
            try:
                i = Instrument.objects.get(id=instrument)
                calibration_event.calibrated_with.add(i)
            except ObjectDoesNotExist:
                raise ValidationError("Could not have calibrated using this instrument. Instrument does not exist.")

        calibration_event.save(using=self.db)
        return calibration_event

    def create_for_import(
            self,
            user=None,
            instrument=None,
            date=None,
            comment=None,
    ):
        if comment is None:
            comment = ''

        calibration_event = CalibrationEvent(
            instrument=instrument,
            user=user,
            date=date,
            comment=comment,
            additional_evidence=None,
            load_bank_data='',
            guided_hardware_data='',
            custom_data='',
        )
        calibration_event.full_clean()
        calibration_event.save(using=self.db)

        approval_data = ApprovalData(
            calibration_event=calibration_event,
            approved=True,
            approver=user,
            date=datetime.utcnow().astimezone(),
            comment='',
        )

        approval_data.save(using=self.db)
        calibration_event.approval_data = approval_data
        calibration_event.save(using=self.db)
        return calibration_event

    def pending_approval(self):
        return self.filter(approval_data=None)

    def find_calibration_event(self, pk, date):
        """ Given an instrument pk and a date, return most recent calibration event valid at that date """
        expression = ExpressionWrapper(F('date') + F('instrument__model__calibration_frequency'),
                                       output_field=DateField())
        return self.filter(instrument__pk=pk).filter(approval_data__approved=True).filter(date__lte=date)\
                   .annotate(expiration=expression).filter(expiration__gte=date).order_by('-date').first()

    def find_valid_calibration_event(self, pk):
        return self.filter(instrument__pk=pk).filter(approval_data__approved=True).order_by('-date').first()


def instrument_evidence_directory_path(instance, filename):
    """ Returns file upload path """
    return f'instrument_{instance.instrument.pk}/{instance.date}/{filename}'


class CalibrationEvent(models.Model):
    """
    Upload a file: The user may attach a single file of type JPG, PNG, GIF, PDF, or XLSX. Files larger than 32 MB must
    be rejected. Allowed for all models.
    """
    instrument = models.ForeignKey(Instrument, related_name='calibration_history', on_delete=models.CASCADE)
    date = models.DateTimeField(validators=[validate_max_date])
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, null=True)
    additional_evidence = models.FileField(upload_to=instrument_evidence_directory_path,
                                           blank=True,
                                           null=True,
                                           validators=[
                                               FileExtensionValidator(['jpg', 'png', 'PNG', 'gif', 'pdf', 'xlsx'])])
    load_bank_data = models.TextField(blank=True, default='')
    guided_hardware_data = models.TextField(blank=True, default='')
    custom_data = models.TextField(blank=True, default='')
    calibrated_with = models.ManyToManyField(Instrument, related_name="used_to_calibrate")
    objects = CalibrationEventManager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return CALIBRATION_EVENT_TEMPLATE.format(self)

    def clean(self):
        if not self.instrument.is_calibratable():
            raise ValidationError("Cannot add Calibration Event to Instrument whose Model cannot be calibrated")


class ApprovalData(models.Model):
    calibration_event = models.OneToOneField(CalibrationEvent, related_name="approval_data", on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    approver = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateTimeField(validators=[validate_max_date])
    comment = models.CharField(max_length=COMMENT_LENGTH, blank=True, default='')

    class Meta:
        ordering = ['-date']
