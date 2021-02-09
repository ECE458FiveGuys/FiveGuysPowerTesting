from rest_framework import viewsets
from rest_framework import permissions

from django_filters.rest_framework import DjangoFilterBackend

from database.model_enums import EquipmentModelEnum, InstrumentEnum
from database.models import EquipmentModel, Instrument, CalibrationEvent
from database.serializers import EquipmentModelSerializer, InstrumentSerializer, CalibrationEventSerializer


class EquipmentModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = EquipmentModel.objects.all()
    serializer_class = EquipmentModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [EquipmentModelEnum.VENDOR.value,
                        EquipmentModelEnum.MODEL_NUMBER.value,
                        EquipmentModelEnum.DESCRIPTION.value]


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['model__' + EquipmentModelEnum.VENDOR.value,
                        'model__' + EquipmentModelEnum.MODEL_NUMBER.value,
                        'model__' + EquipmentModelEnum.DESCRIPTION.value,
                        InstrumentEnum.SERIAL_NUMBER.value]
    search_fields = ['model__' + EquipmentModelEnum.VENDOR.value,
                     'model__' + EquipmentModelEnum.MODEL_NUMBER.value,
                     'model__' + EquipmentModelEnum.DESCRIPTION.value]


class CalibrationEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = CalibrationEvent.objects.all()
    serializer_class = CalibrationEventSerializer
    permission_classes = [permissions.IsAuthenticated]
