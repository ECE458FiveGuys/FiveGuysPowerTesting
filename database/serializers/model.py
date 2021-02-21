from datetime import timedelta

from rest_framework import serializers

from database.model_enums import CategoryEnum, ModelEnum
from database.models.model import Model
from database.models.model_category import ModelCategory
from database.serializers.instrument import InstrumentSerialNumberSerializer


class ModelCategoryRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCategory
        fields = [e.value for e in CategoryEnum]


class ModelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCategory
        fields = [e.value for e in CategoryEnum]


class ModelRetrieveSerializer(serializers.ModelSerializer):
    model_categories = ModelCategorySerializer(many=True, read_only=True)
    instruments = InstrumentSerialNumberSerializer(many=True, read_only=True)

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
    calibration_frequency = serializers.IntegerField(required=False)

    class Meta:
        model = Model
        fields = [e.value for e in ModelEnum]
        depth = 2

    def create(self, validated_data):
        try:
            calibration_frequency_data = validated_data.pop('calibration_frequency')
            calibration_frequency = timedelta(days=calibration_frequency_data)
        except KeyError:
            calibration_frequency = timedelta(days=0)
        model_categories_data = validated_data.pop('model_categories')
        model = Model.objects.create(**validated_data, calibration_frequency=calibration_frequency)
        for model_category_data in model_categories_data:
            model.model_categories.add(ModelCategory.objects.get(name=model_category_data))
        return model


class ModelSerializer(ModelBaseSerializer):
    def to_representation(self, instance):
        try:
            return ModelListSerializer(instance).data
        except AttributeError:
            return ModelBaseSerializer(instance).data


class VendorAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = [ModelEnum.VENDOR.value]


class ModelAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = [ModelEnum.MODEL_NUMBER.value]
