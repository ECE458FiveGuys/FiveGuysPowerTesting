from rest_framework import serializers
from datetime import datetime

from database.enums import ApprovalDataEnum, CalibrationEventEnum, InstrumentEnum, ModelEnum
from database.models.instrument import ApprovalData, CalibrationEvent, Instrument
from database.models.model import Model
from user_portal.serializers import UserFieldsForCalibrationEventSerializer, UserForApprovalDataSerializer


class ModelForInstrumentForCalibrationRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = [
            ModelEnum.PK,
            ModelEnum.MODEL_NUMBER.value,
            ModelEnum.VENDOR.value,
            ModelEnum.DESCRIPTION.value,
        ]


class InstrumentForCalibrationRetrieveSerializer(serializers.ModelSerializer):
    model = ModelForInstrumentForCalibrationRetrieveSerializer(read_only=True)

    class Meta:
        model = Instrument
        fields = [
            InstrumentEnum.PK.value,
            InstrumentEnum.SERIAL_NUMBER.value,
            InstrumentEnum.ASSET_TAG_NUMBER.value,
            InstrumentEnum.MODEL.value
        ]


class InstrumentForCalibrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [
            InstrumentEnum.PK.value,
            InstrumentEnum.SERIAL_NUMBER.value,
            InstrumentEnum.ASSET_TAG_NUMBER.value,
        ]


class InstrumentsPendingApprovalSerializer(serializers.ModelSerializer):
    instrument = InstrumentForCalibrationEventSerializer(many=False, read_only=True)

    class Meta:
        model = CalibrationEvent
        fields = [
            CalibrationEventEnum.PK.value,
            CalibrationEventEnum.INSTRUMENT.value,
        ]


class ApprovalDataSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = ApprovalData
        fields = [e.value for e in ApprovalDataEnum]

    def validate(self, attrs):
        if 'calibration_event' in attrs:
            if not attrs['calibration_event'].instrument.model.approval_required:
                raise serializers.ValidationError(
                    "Cannot approve a calibration event for a model whose calibration does not require approval.")
        return attrs

    def create(self, validated_data):
        validated_data['date'] = datetime.utcnow().astimezone()
        return super().create(validated_data)


class ApprovalDataRetrieveSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    approver = UserForApprovalDataSerializer()

    class Meta:
        model = ApprovalData
        fields = [e.value for e in ApprovalDataEnum]


class CalibrationRetrieveSerializer(serializers.ModelSerializer):
    instrument = InstrumentForCalibrationRetrieveSerializer(read_only=True)
    user = UserFieldsForCalibrationEventSerializer(many=False, read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    approval_data = ApprovalDataRetrieveSerializer(many=False, read_only=True)
    calibrated_with = InstrumentForCalibrationEventSerializer(many=True, read_only=True)

    class Meta:
        model = CalibrationEvent
        fields = [e.value for e in CalibrationEventEnum]


class CalibrationHistorySerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = CalibrationEvent
        fields = [
            CalibrationEventEnum.PK.value,
            CalibrationEventEnum.DATE.value,
        ]


class CalibrationEventSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    approval_data = ApprovalDataRetrieveSerializer(many=False, read_only=True)
    calibrated_with = serializers.SlugRelatedField(queryset=Instrument.objects.all(), many=True,
                                                   slug_field='asset_tag_number', required=False)

    class Meta:
        model = CalibrationEvent
        fields = [e.value for e in CalibrationEventEnum]

    def validate(self, attrs):
        if 'instrument' in attrs:
            calibration_mode = attrs['instrument'].model.calibration_mode
            if calibration_mode == 'NOT_CALIBRATABLE':
                raise serializers.ValidationError(
                    'Instrument whose model is not calibratable may not have a calibration'
                    ' event associated with it.')
            if CalibrationEventEnum.LOAD_BANK_DATA.value in attrs:
                if calibration_mode in {'DEFAULT', 'GUIDED_HARDWARE', 'CUSTOM'}:
                    raise serializers.ValidationError('Model needs calibration mode of LOAD_BANK in order to have input'
                                                      ' from the load calibration wizard.')
            if CalibrationEventEnum.GUIDED_HARDWARE_DATA.value in attrs:
                if calibration_mode in {'DEFAULT', 'LOAD_BANK', 'CUSTOM'}:
                    raise serializers.ValidationError(
                        'Model needs calibration mode of GUIDED_HARDWARE in order to have '
                        'input from the guided hardware wizard.')
            if 'date' in attrs:
                attrs['date'] = attrs['date'].astimezone()
        return attrs
