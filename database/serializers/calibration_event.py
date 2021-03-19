from rest_framework import serializers

from database.enums import CalibrationEventEnum
from database.models.instrument import CalibrationEvent
from user_portal.serializers import UserFieldsForCalibrationEventSerializer


class CalibrationHistoryRetrieveSerializer(serializers.ModelSerializer):
    user = UserFieldsForCalibrationEventSerializer(many=False, read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = CalibrationEvent
        fields = [CalibrationEventEnum.PK.value,
                  CalibrationEventEnum.DATE.value,
                  CalibrationEventEnum.USER.value,
                  CalibrationEventEnum.COMMENT.value,
                  CalibrationEventEnum.ADDITIONAL_EVIDENCE.value,
                  CalibrationEventEnum.LOAD_BANK_DATA.value,
                  CalibrationEventEnum.GUIDED_HARDWARE_DATA.value, ]


class CalibrationHistorySerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = CalibrationEvent
        fields = [CalibrationEventEnum.PK.value,
                  CalibrationEventEnum.DATE.value]


class CalibrationEventSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])

    class Meta:
        model = CalibrationEvent
        fields = [e.value for e in CalibrationEventEnum]

    def validate(self, attrs):
        calibration_mode = attrs['instrument'].model.calibration_mode
        if calibration_mode == 'NOT_CALIBRATABLE':
            raise serializers.ValidationError('Instrument whose model is not calibratable may not have a calibration'
                                              ' event associated with it.')
        if CalibrationEventEnum.LOAD_BANK_DATA.value in attrs:
            if calibration_mode in {'DEFAULT', 'GUIDED_HARDWARE_DATA'}:
                raise serializers.ValidationError('Model needs calibration mode of LOAD_BANK in order to have input'
                                                  ' from the load calibration wizard.')
        if CalibrationEventEnum.GUIDED_HARDWARE_DATA.value in attrs:
            if calibration_mode in {'DEFAULT', 'LOAD_BANK_DATA'}:
                raise serializers.ValidationError('Model needs calibration mode of GUIDED_HARDWARE in order to have '
                                                  'input from the guided hardware wizard.')
        return attrs

    def create(self, validated_data):
        validated_data['date'] = validated_data['date'].astimezone()
        return super().create(validated_data)
