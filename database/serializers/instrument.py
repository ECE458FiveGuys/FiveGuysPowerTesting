from rest_framework import serializers

from database.model_enums import CategoryEnum, InstrumentEnum, ModelEnum
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
                  ModelEnum.MODEL_CATEGORIES.value]


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
        instrument_categories_data = validated_data.pop('instrument_categories')
        instrument = Instrument.objects.create(**validated_data)
        for instrument_category_data in instrument_categories_data:
            instrument.instrument_categories.add(InstrumentCategory.objects.get(name=instrument_category_data))
        return instrument


class InstrumentSerializer(InstrumentBaseSerializer):
    def to_representation(self, instance):
        try:
            return InstrumentListSerializer(instance).data
        except AttributeError:
            return InstrumentBaseSerializer(instance).data
