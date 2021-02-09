from rest_framework import viewsets
from rest_framework import permissions

from django_filters.rest_framework import DjangoFilterBackend

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
    filterset_fields = ['vendor']


# class EquipmentModelFilterList(generics.ListAPIView):
#     serializer_class = EquipmentModelSerializer
#
#     def get_queryset(self):
#         queryset = EquipmentModel.objects.all()
#         vendor = self.request.query_params.get('vendor', None)
#         if vendor is not None:
#             queryset = queryset.filter(equipmentmodel__vendor=vendor)
#         return queryset


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class CalibrationEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = CalibrationEvent.objects.all()
    serializer_class = CalibrationEventSerializer
    permission_classes = [permissions.IsAuthenticated]
