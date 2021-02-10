from django.db.migrations import serializer
from django.db.models import Q
from rest_framework import permissions, serializers
from rest_framework import viewsets, generics

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from database.model_enums import EquipmentModelEnum, InstrumentEnum
from database.models import EquipmentModel, Instrument, CalibrationEvent
from database.serializers import EquipmentModelSerializer, InstrumentSerializer, CalibrationEventSerializer, \
    VendorSerializer


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


class VendorAutoCompleteViewSet(generics.ListAPIView):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EquipmentModel.objects.filter(
            Q(vendor__contains=self.request.query_params.get('vendor'))
        )

    def list(self, request):
        vendor_list = list({model.vendor for model in self.get_queryset()})
        vendor_list.sort()
        vendor_list[:]
        return Response(vendor_list)


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


class CalibrationEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = CalibrationEvent.objects.all()
    serializer_class = CalibrationEventSerializer
    permission_classes = [permissions.IsAuthenticated]
