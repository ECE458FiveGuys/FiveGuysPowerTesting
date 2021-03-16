from datetime import timedelta

import django.core.exceptions
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from database.enums import CategoryEnum, InstrumentEnum, ModelEnum
from database.models.instrument import Instrument
from database.models.model import Model
from database.models.model_category import ModelCategory


class InstrumentForModelRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value,
                  InstrumentEnum.SERIAL_NUMBER.value,
                  InstrumentEnum.ASSET_TAG_NUMBER.value]


class ModelUniqueFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = [ModelEnum.PK.value,
                  ModelEnum.VENDOR.value,
                  ModelEnum.MODEL_NUMBER.value]


class ModelCategoryRetrieveSerializer(serializers.ModelSerializer):
    model_list = ModelUniqueFieldsSerializer(many=True, read_only=True)

    class Meta:
        model = ModelCategory
        fields = [e.value for e in CategoryEnum] + ['model_list']


class ModelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCategory
        fields = [e.value for e in CategoryEnum]


class ModelRetrieveSerializer(serializers.ModelSerializer):
    model_categories = ModelCategorySerializer(many=True, read_only=True)
    instruments = InstrumentForModelRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Model
        fields = [e.value for e in ModelEnum] + ['instruments']


class ModelListSerializer(serializers.ModelSerializer):
    model_categories = ModelCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Model
        fields = [ModelEnum.PK.value,
                  ModelEnum.VENDOR.value,
                  ModelEnum.MODEL_NUMBER.value,
                  ModelEnum.DESCRIPTION.value,
                  ModelEnum.CALIBRATION_FREQUENCY.value,
                  ModelEnum.MODEL_CATEGORIES.value]


class ModelBaseSerializer(serializers.ModelSerializer):
    model_categories = serializers.SlugRelatedField(queryset=ModelCategory.objects.all(), many=True, slug_field='name',
                                                    required=False)
    calibration_frequency = serializers.IntegerField(required=False, min_value=0, max_value=3653)

    class Meta:
        model = Model
        fields = [e.value for e in ModelEnum]

    def create(self, validated_data):
        try:
            calibration_frequency_data = validated_data.pop('calibration_frequency')
            calibration_frequency = timedelta(days=calibration_frequency_data)
        except KeyError:
            calibration_frequency = timedelta(days=0)
        try:
            model_categories_data = validated_data.pop('model_categories')
        except KeyError:
            model_categories_data = []
        validated_data['calibration_frequency'] = calibration_frequency
        try:
            model = Model.objects.create(**validated_data)
        except django.core.exceptions.ValidationError as e:
            raise ValidationError(e.messages)
        for model_category_data in model_categories_data:
            model.model_categories.add(ModelCategory.objects.get(name=model_category_data))
        return model

    def validate(self, attrs):
        if self.partial:
            if ModelEnum.CALIBRATION_FREQUENCY.value not in attrs:
                if self.instance.calibration_frequency == timedelta(days=0):
                    if ModelEnum.CALIBRATION_MODE.value in attrs and attrs[ModelEnum.CALIBRATION_MODE.value] in {'DEFAULT', 'LOAD_BANK'}:
                        raise serializers.ValidationError('Non-calibratable model cannot have a calibration mode')
        else:
            if ModelEnum.CALIBRATION_FREQUENCY.value not in attrs or attrs[ModelEnum.CALIBRATION_FREQUENCY.value] == 0:
                if ModelEnum.CALIBRATION_MODE.value in attrs and attrs[ModelEnum.CALIBRATION_MODE.value] in {'DEFAULT', 'LOAD_BANK'}:
                    raise serializers.ValidationError('Non-calibratable model cannot have a calibration mode')
        return attrs

    def update(self, instance, validated_data):
        try:
            calibration_frequency_data = validated_data.pop('calibration_frequency')
            calibration_frequency = timedelta(days=calibration_frequency_data)
        except KeyError:
            calibration_frequency = instance.calibration_frequency
        model_categories = []
        try:
            model_categories_data = validated_data.pop('model_categories')
            for model_category_data in model_categories_data:
                model_categories.append(ModelCategory.objects.get(name=model_category_data))
        except KeyError:
            model_categories = instance.model_categories.all()
        instance.vendor = validated_data.get(ModelEnum.VENDOR.value, instance.vendor)
        instance.model_number = validated_data.get(ModelEnum.MODEL_NUMBER.value, instance.model_number)
        instance.description = validated_data.get(ModelEnum.DESCRIPTION.value, instance.description)
        instance.comment = validated_data.get(ModelEnum.COMMENT.value, instance.comment)
        instance.calibration_frequency = calibration_frequency
        instance.calibration_mode = validated_data.get(ModelEnum.CALIBRATION_MODE.value, instance.calibration_mode)
        instance.model_categories.set(model_categories)
        instance.full_clean()
        instance.save()
        return instance


class ModelSerializer(ModelBaseSerializer):
    def to_representation(self, instance):
        try:
            return ModelListSerializer(instance).data
        except AttributeError:
            return ModelBaseSerializer(instance).data
