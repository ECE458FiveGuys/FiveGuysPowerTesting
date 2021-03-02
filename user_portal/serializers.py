from rest_framework import serializers
from djoser import serializers as s

from user_portal.models import PowerUser as User
from djoser.conf import settings


class UserFieldsForCalibrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'name']


class CustomUserSerializer(s.UserSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            'is_staff'
        )
        read_only_fields = (settings.LOGIN_FIELD, 'is_staff')


class IsStaffSerializer(serializers.Serializer):
    is_staff = serializers.BooleanField(required=True)
