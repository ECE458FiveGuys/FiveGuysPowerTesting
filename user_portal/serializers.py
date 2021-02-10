from rest_framework import serializers

from user_portal.models import PowerUser


class UserFieldsForCalibrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerUser
        fields = ['pk', 'username', 'name']
