from rest_framework import serializers

from database.model_enums import InstrumentEnum, ModelEnum
from database.models.model import Model
from database.models.instrument import Instrument
from database.serializers.calibration_event import CalibrationHistoryRetrieveSerializer


class ModelForInstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = [ModelEnum.PK.value,
                  ModelEnum.VENDOR.value,
                  ModelEnum.MODEL_NUMBER.value,
                  ModelEnum.DESCRIPTION.value]


class InstrumentSerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value, InstrumentEnum.SERIAL_NUMBER.value]


class InstrumentRetrieveSerializer(serializers.ModelSerializer):
    calibration_expiration_date = serializers.DateField()
    calibration_history = CalibrationHistoryRetrieveSerializer(many=True, read_only=True)
    model = ModelForInstrumentSerializer(many=False, read_only=True)

    class Meta:
        model = Instrument
        fields = [e.value for e in InstrumentEnum] + ['calibration_history', 'calibration_expiration_date']


class InstrumentListSerializer(serializers.ModelSerializer):
    most_recent_calibration_date = serializers.DateField()
    calibration_expiration_date = serializers.DateField()
    model = ModelForInstrumentSerializer(many=False, read_only=True)

    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value,
                  InstrumentEnum.MODEL.value,
                  InstrumentEnum.SERIAL_NUMBER.value,
                  'most_recent_calibration_date',
                  'calibration_expiration_date']


class InstrumentBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value,
                  InstrumentEnum.MODEL.value,
                  InstrumentEnum.SERIAL_NUMBER.value,
                  InstrumentEnum.COMMENT.value]


class InstrumentSerializer(InstrumentBaseSerializer):
    def to_representation(self, instance):
        try:
            return InstrumentListSerializer(instance).data
        except AttributeError:
            return InstrumentBaseSerializer(instance).data
