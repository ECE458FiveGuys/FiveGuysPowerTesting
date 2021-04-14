import django.core.exceptions
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser import serializers as s
from djoser.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user_portal.enums import PermissionGroupEnum, UserEnum
from user_portal.models import User


class UserFieldsForCalibrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            UserEnum.PK.value,
            UserEnum.USERNAME.value,
        ]


class UserForApprovalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            UserEnum.PK.value,
            UserEnum.NAME.value,
            UserEnum.USERNAME.value,
            UserEnum.EMAIL.value,
        ]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class CustomUserSerializer(s.UserSerializer):
    groups = serializers.SlugRelatedField(queryset=Group.objects.all(), many=True, slug_field='name', required=False)

    class Meta:
        model = User
        fields = (settings.USER_ID_FIELD, settings.LOGIN_FIELD,) + tuple(User.REQUIRED_FIELDS) + (
            UserEnum.IS_STAFF.value,
            UserEnum.GROUPS.value,
        )
        read_only_fields = (settings.LOGIN_FIELD, 'is_staff')

    def validate(self, attrs):
        if "username" in attrs and attrs["username"].find("@") != -1:
            raise serializers.ValidationError("Usernames may not contain '@' character")
        return attrs

    def update(self, instance, validated_data):
        groups = []
        try:
            groups_data = validated_data.pop('groups')
            for group_data in groups_data:
                groups.append(Group.objects.get(name=group_data))
        except KeyError:
            groups = instance.groups.all()
        instance.groups.set(groups)
        instance.save()
        return super().update(instance, validated_data)


class CustomUserCreateSerializer(s.UserCreateSerializer):
    groups = serializers.SlugRelatedField(queryset=Group.objects.all(), many=True, slug_field='name', required=False)

    class Meta:
        model = User
        fields = (settings.USER_ID_FIELD, settings.LOGIN_FIELD,) + tuple(User.REQUIRED_FIELDS) + (
            UserEnum.GROUPS.value,
            "password",
        )

    def validate(self, attrs):
        try:
            groups = attrs.pop('groups')
        except KeyError:
            groups = [PermissionGroupEnum.UNPRIVILEGED.value]
        user = User(**attrs)
        attrs['groups'] = groups
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

    def create(self, validated_data):
        groups_data = validated_data.pop('groups')
        try:
            user = User.objects.create_user(**validated_data)
        except django.core.exceptions.ValidationError as e:
            raise ValidationError(e.messages)
        for group_data in groups_data:
            user.groups.add(Group.objects.get(name=group_data))
        return user


class IsStaffSerializer(serializers.Serializer):
    is_staff = serializers.BooleanField(required=True)
