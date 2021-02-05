from rest_framework import serializers

from database.model_enums import UserEnum, ModelEnum, InstrumentEnum, CalibrationEventEnum
from database.models import User, Model, Instrument, CalibrationEvent


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [e.value for e in UserEnum]


class ModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Model
        fields = [e.value for e in ModelEnum]


class InstrumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Instrument
        fields = [e.value for e in InstrumentEnum]


class CalibrationEventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CalibrationEvent
        fields = [e.value for e in CalibrationEventEnum]
