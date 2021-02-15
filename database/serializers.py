from datetime import timedelta

from rest_framework import serializers

from database.model_enums import EquipmentModelEnum, InstrumentEnum, CalibrationEventEnum
from database.models import EquipmentModel, Instrument, CalibrationEvent
from user_portal.serializers import UserFieldsForCalibrationEventSerializer


class EquipmentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModel
        fields = [e.value for e in EquipmentModelEnum]


class InstrumentSerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value, InstrumentEnum.SERIAL_NUMBER.value]


class EquipmentModelRetrieveSerializer(serializers.ModelSerializer):
    instruments = InstrumentSerialNumberSerializer(many=True, read_only=True)

    class Meta:
        model = EquipmentModel
        fields = [e.value for e in EquipmentModelEnum] + ['instruments']


class EquipmentModelForInstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModel
        fields = [EquipmentModelEnum.PK.value,
                  EquipmentModelEnum.VENDOR.value,
                  EquipmentModelEnum.MODEL_NUMBER.value,
                  EquipmentModelEnum.DESCRIPTION.value]


class CalibrationHistoryRetrieveSerializer(serializers.ModelSerializer):
    user = UserFieldsForCalibrationEventSerializer(many=False, read_only=True)

    class Meta:
        model = CalibrationEvent
        fields = [CalibrationEventEnum.PK.value,
                  CalibrationEventEnum.DATE.value,
                  CalibrationEventEnum.USER.value,
                  CalibrationEventEnum.COMMENT.value]


class CalibrationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationEvent
        fields = [CalibrationEventEnum.PK.value,
                  CalibrationEventEnum.DATE.value]


class InstrumentRetrieveSerializer(serializers.ModelSerializer):
    calibration_expiration_date = serializers.DateField()
    calibration_history = CalibrationHistoryRetrieveSerializer(many=True, read_only=True)
    model = EquipmentModelForInstrumentSerializer(many=False, read_only=True)

    class Meta:
        model = Instrument
        fields = [e.value for e in InstrumentEnum] + ['calibration_history', 'calibration_expiration_date']


class InstrumentListSerializer(serializers.ModelSerializer):
    most_recent_calibration_date = serializers.DateField()
    calibration_expiration_date = serializers.DateField()
    model = EquipmentModelForInstrumentSerializer(many=False, read_only=True)

    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value,
                  InstrumentEnum.MODEL.value,
                  InstrumentEnum.SERIAL_NUMBER.value,
                  'most_recent_calibration_date',
                  'calibration_expiration_date']


class InstrumentBaseSerializer(serializers.ModelSerializer):
    calibration_history = CalibrationHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value,
                  InstrumentEnum.SERIAL_NUMBER.value,
                  InstrumentEnum.MODEL.value] + ['calibration_history']


class InstrumentSerializer(InstrumentBaseSerializer):
    def to_representation(self, instance):
        try:
            return InstrumentListSerializer(instance).data
        except AttributeError:
            return InstrumentBaseSerializer(instance).data


class CalibrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationEvent
        fields = [e.value for e in CalibrationEventEnum]


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModel
        fields = [EquipmentModelEnum.VENDOR.value]
