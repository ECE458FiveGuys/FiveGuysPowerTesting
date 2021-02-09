from rest_framework import serializers

from database.model_enums import EquipmentModelEnum, InstrumentEnum, CalibrationEventEnum, PostEnum
from database.models import EquipmentModel, Instrument, CalibrationEvent


class InstrumentSerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value, InstrumentEnum.SERIAL_NUMBER.value]


class EquipmentModelSerializer(serializers.ModelSerializer):
    instruments = InstrumentSerialNumberSerializer(many=True, read_only=True)

    class Meta:
        model = EquipmentModel
        fields = [e.value for e in EquipmentModelEnum]


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [e.value for e in InstrumentEnum]


class CalibrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationEvent
        fields = [e.value for e in CalibrationEventEnum]


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModel
        fields = [EquipmentModelEnum.VENDOR.value]
