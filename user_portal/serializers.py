import django.core.exceptions
from django.contrib.auth.password_validation import validate_password
from djoser import serializers as s
from django.core import exceptions as django_exceptions
from djoser.conf import settings
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user_portal.models import PowerUser as User


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


class CustomUserCreateSerializer(s.UserCreateSerializer):
    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )
        if "username" in attrs and attrs["username"].find("@") != -1:
            raise serializers.ValidationError("Usernames may not contain '@' character")

        return attrs

class IsStaffSerializer(serializers.Serializer):
    is_staff = serializers.BooleanField(required=True)
