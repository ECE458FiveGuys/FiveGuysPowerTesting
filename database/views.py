from django.db.models import Q
from rest_framework import permissions
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from database.model_enums import EquipmentModelEnum, InstrumentEnum
from database.models import EquipmentModel, Instrument, CalibrationEvent
from database.serializers import EquipmentModelSerializer, InstrumentSerializer, CalibrationEventSerializer, \
    VendorSerializer, InstrumentRetrieveSerializer, EquipmentModelRetrieveSerializer


class EquipmentModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = EquipmentModel.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = [
        EquipmentModelEnum.VENDOR.value,
        EquipmentModelEnum.MODEL_NUMBER.value,
        EquipmentModelEnum.DESCRIPTION.value
    ]
    search_fields = [
        EquipmentModelEnum.VENDOR.value,
        EquipmentModelEnum.MODEL_NUMBER.value,
        EquipmentModelEnum.DESCRIPTION.value,
        EquipmentModelEnum.CALIBRATION_FREQUENCY.value
    ]
    ordering_fields = [
        EquipmentModelEnum.VENDOR.value,
        EquipmentModelEnum.MODEL_NUMBER.value
    ]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EquipmentModelRetrieveSerializer  # 2.1.4
        return EquipmentModelSerializer  # 2.1.3

    @action(detail=False, methods=['get'])
    def all(self, request):
        return Response(EquipmentModelSerializer(self.queryset, many=True).data)


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

    def list(self, request, **kwargs):
        vendor_list = list({model.vendor for model in self.get_queryset()})
        vendor_list.sort()
        return Response(vendor_list)


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Instrument.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = [
        'model__' + EquipmentModelEnum.VENDOR.value,
        'model__' + EquipmentModelEnum.MODEL_NUMBER.value,
        'model__' + EquipmentModelEnum.DESCRIPTION.value,
        InstrumentEnum.SERIAL_NUMBER.value
    ]
    search_fields = [
        'model__' + EquipmentModelEnum.VENDOR.value,
        'model__' + EquipmentModelEnum.MODEL_NUMBER.value,
        'model__' + EquipmentModelEnum.DESCRIPTION.value,
        InstrumentEnum.SERIAL_NUMBER.value
    ]
    ordering_fields = [
        'model__' + EquipmentModelEnum.VENDOR.value,
        'model__' + EquipmentModelEnum.MODEL_NUMBER.value,
        'model__' + EquipmentModelEnum.DESCRIPTION.value,
        InstrumentEnum.MODEL.value,
        InstrumentEnum.SERIAL_NUMBER.value,
        InstrumentEnum.COMMENT.value
    ]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InstrumentRetrieveSerializer  # 2.2.4
        return InstrumentSerializer  # 2.2.3

    @action(detail=False, methods=['get'])
    def all(self, request):
        return Response(InstrumentSerializer(self.queryset, many=True).data)


class CalibrationEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = CalibrationEvent.objects.all()
    serializer_class = CalibrationEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = []

    @action(detail=False, methods=['get'])
    def all(self, request):
        return Response(InstrumentSerializer(self.queryset, many=True).data)
