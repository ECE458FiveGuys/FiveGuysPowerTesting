from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import connections, models, transaction
from django.db.models.fields import AutoField
from django.utils.functional import partition

from database.constants import COMMENT_LENGTH, DESCRIPTION_LENGTH, MODEL_NUMBER_LENGTH, VENDOR_LENGTH
from database.exceptions import CHARACTER_LENGTH_ERROR_MESSAGE, ModelFieldLengthException, \
    ModelRequiredFieldsEmptyException, NULL_FIELD_ERROR_MESSAGE, UserError
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
        if calibration_frequency is None:
            calibration_frequency = timedelta(days=0)
        if model_categories is None:
            model_categories = []
        if calibration_mode is None:
            calibration_mode = 'FILE'
        try:
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

    def bulk_create(self, objs, batch_size=None):
        """
        Insert each of the instances into the database. Do *not* call
        save() on each of the instances, do not send any pre/post_save
        signals, and do not set the primary key attribute if it is an
        autoincrement field.
        """
        assert batch_size is None or batch_size > 0
        self._for_write = True
        fields = self.model._meta.concrete_fields
        objs = list(objs)
        self._populate_pk_values(objs)
        with transaction.atomic(using=self.db, savepoint=False):
            objs_with_pk, objs_without_pk = partition(lambda o: o.pk is None, objs)
            if objs_without_pk:
                fields = [f for f in fields if not isinstance(f, AutoField)]
                ids = self._batched_insert(objs_without_pk, fields, batch_size)
                for obj_without_pk, pk in zip(objs_without_pk, ids):
                    obj_without_pk.pk = pk
                    obj_without_pk._state.adding = False
                    obj_without_pk._state.db = self.db

        return objs

    def _batched_insert(self, objs, fields, batch_size):
        """
        Helper method for bulk_create() to insert objs one batch at a time.
        """
        ops = connections[self.db].ops
        batch_size = (batch_size or max(ops.bulk_batch_size(fields, objs), 1))
        inserted_ids = []
        for item in [objs[i:i + batch_size] for i in range(0, len(objs), batch_size)]:
            self._insert(item, fields=fields, using=self.db)
        return inserted_ids

    def _populate_pk_values(self, objs):
        for obj in objs:
            if obj.pk is None:
                obj.pk = obj._meta.pk.get_pk_value_on_save(obj)

    def vendors(self):
        return self.order_by().values_list('vendor', flat=True).distinct()

    def models_for_vendor(self, vendor):
        return self.order_by().filter(vendor=vendor).values_list('model_number', flat=True).distinct()

    def models(self):
        return self.order_by().values_list('model_number', flat=True).distinct()


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
    calibration_frequency = models.DurationField(blank=True,
                                                 default=timedelta(days=0),
                                                 validators=[MinValueValidator(timedelta(days=0)),
                                                             MaxValueValidator(timedelta(days=3653))])
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
