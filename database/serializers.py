from rest_framework import serializers

from database.model_enums import ModelEnum, InstrumentEnum, CalibrationEventEnum, PostEnum
from database.models import Model, Instrument, CalibrationEvent


# class UserSerializer(serializers.Serializer):
#     id = serializers.IntegerField(default=0)
#     username = serializers.CharField()
#     name = serializers.CharField()
#     email = serializers.EmailField()
#     password = serializers.CharField()
#     admin = serializers.BooleanField()
#     active = serializers.BooleanField()


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
