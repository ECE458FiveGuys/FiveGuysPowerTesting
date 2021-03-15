import django.core.exceptions
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from database.enums import CategoryEnum, InstrumentEnum, ModelEnum
from database.models.instrument_category import InstrumentCategory
from database.models.model import Model
from database.models.instrument import Instrument
from database.serializers.calibration_event import CalibrationHistoryRetrieveSerializer
from database.serializers.model import ModelCategorySerializer


class ModelForInstrumentSerializer(serializers.ModelSerializer):
    model_categories = ModelCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Model
        fields = [ModelEnum.PK.value,
                  ModelEnum.VENDOR.value,
                  ModelEnum.MODEL_NUMBER.value,
                  ModelEnum.DESCRIPTION.value,
                  ModelEnum.MODEL_CATEGORIES.value,
                  ModelEnum.CALIBRATION_MODE.value]


class InstrumentUniqueFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value]


class InstrumentCategoryRetrieveSerializer(serializers.ModelSerializer):
    instrument_list = InstrumentUniqueFieldsSerializer(many=True, read_only=True)

    class Meta:
        model = InstrumentCategory
        fields = [e.value for e in CategoryEnum] + ['model_list']


class InstrumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentCategory
        fields = [e.value for e in CategoryEnum]


class InstrumentRetrieveSerializer(serializers.ModelSerializer):
    calibration_expiration_date = serializers.DateField()
    calibration_history = CalibrationHistoryRetrieveSerializer(many=True, read_only=True)
    model = ModelForInstrumentSerializer(many=False, read_only=True)
    instrument_categories = InstrumentCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Instrument
        fields = [e.value for e in InstrumentEnum] + ['calibration_history', 'calibration_expiration_date']


class InstrumentBulkImportSerializer(serializers.ModelSerializer):
    model = ModelForInstrumentSerializer(many=False, read_only=True)
    instrument_categories = InstrumentCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Instrument
        fields = [e.value for e in InstrumentEnum]


class InstrumentListSerializer(serializers.ModelSerializer):
    most_recent_calibration_date = serializers.DateField()
    calibration_expiration_date = serializers.DateField()
    model = ModelForInstrumentSerializer(many=False, read_only=True)
    instrument_categories = InstrumentCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value,
                  InstrumentEnum.MODEL.value,
                  InstrumentEnum.SERIAL_NUMBER.value,
                  InstrumentEnum.ASSET_TAG_NUMBER.value,
                  InstrumentEnum.INSTRUMENT_CATEGORIES.value,
                  'most_recent_calibration_date',
                  'calibration_expiration_date']


class InstrumentBaseSerializer(serializers.ModelSerializer):
    instrument_categories = serializers.SlugRelatedField(queryset=InstrumentCategory.objects.all(), many=True,
                                                         slug_field='name', required=False)

    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value,
                  InstrumentEnum.MODEL.value,
                  InstrumentEnum.SERIAL_NUMBER.value,
                  InstrumentEnum.COMMENT.value,
                  InstrumentEnum.ASSET_TAG_NUMBER.value,
                  InstrumentEnum.INSTRUMENT_CATEGORIES.value]

    def create(self, validated_data):
        try:
            instrument_categories_data = validated_data.pop('instrument_categories')
        except KeyError:
            instrument_categories_data = []
        try:
            instrument = Instrument.objects.create(**validated_data)
        except django.core.exceptions.ValidationError as e:
            raise ValidationError(e.messages)
        for instrument_category_data in instrument_categories_data:
            instrument.instrument_categories.add(InstrumentCategory.objects.get(name=instrument_category_data))
        return instrument

    def update(self, instance, validated_data):
        instrument_categories = []
        try:
            instrument_categories_data = validated_data.pop('instrument_categories')
            for instrument_category_data in instrument_categories_data:
                instrument_categories.append(InstrumentCategory.objects.get(name=instrument_category_data))
        except KeyError:
            instrument_categories = instance.instrument_categories.all()
        instance.model = validated_data.get(InstrumentEnum.MODEL.value, instance.model)
        instance.serial_number = validated_data.get(InstrumentEnum.SERIAL_NUMBER.value, instance.serial_number)
        instance.comment = validated_data.get(InstrumentEnum.COMMENT.value, instance.comment)
        instance.asset_tag_number = validated_data.get(InstrumentEnum.ASSET_TAG_NUMBER, instance.asset_tag_number)
        instance.instrument_categories.set(instrument_categories)
        instance.save()
        return instance


class InstrumentSerializer(InstrumentBaseSerializer):
    def to_representation(self, instance):
        try:
            return InstrumentListSerializer(instance).data
        except AttributeError:
            return InstrumentBaseSerializer(instance).data
