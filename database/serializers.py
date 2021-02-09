from rest_framework import serializers

from database.model_enums import EquipmentModelEnum, InstrumentEnum, CalibrationEventEnum
from database.models import EquipmentModel, Instrument, CalibrationEvent


class InstrumentSerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [InstrumentEnum.PK.value, InstrumentEnum.SERIAL_NUMBER.value]


class EquipmentModelSerializer(serializers.ModelSerializer):
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


class CalibrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationEvent
        fields = [e.value for e in CalibrationEventEnum]


class InstrumentSerializerResponse(serializers.ModelSerializer):
    calibration_history = CalibrationEventSerializer(many=True, read_only=True)
    model = EquipmentModelForInstrumentSerializer(many=False, read_only=True)

    class Meta:
        model = Instrument
        fields = [e.value for e in InstrumentEnum] + ['calibration_history']


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [e.value for e in InstrumentEnum]

    def to_representation(self, instance):
        if self.context['request'].method == 'GET':
            serializer = InstrumentSerializerResponse(instance)
            return serializer.data
        return super().to_representation(instance)


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModel
        fields = [EquipmentModelEnum.VENDOR.value]
