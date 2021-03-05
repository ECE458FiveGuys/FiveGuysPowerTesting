from rest_framework import serializers

from database.model_enums import CalibrationEventEnum
from database.models.calibration_event import CalibrationEvent
from user_portal.serializers import UserFieldsForCalibrationEventSerializer


class CalibrationHistoryRetrieveSerializer(serializers.ModelSerializer):
    user = UserFieldsForCalibrationEventSerializer(many=False, read_only=True)

    class Meta:
        model = CalibrationEvent
        fields = [CalibrationEventEnum.PK.value,
                  CalibrationEventEnum.DATE.value,
                  CalibrationEventEnum.USER.value,
                  CalibrationEventEnum.COMMENT.value,
                  CalibrationEventEnum.ADDITIONAL_EVIDENCE.value,
                  CalibrationEventEnum.LOAD_BANK_DATA.value]


class CalibrationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationEvent
        fields = [CalibrationEventEnum.PK.value,
                  CalibrationEventEnum.DATE.value]


class CalibrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationEvent
        fields = [e.value for e in CalibrationEventEnum]
