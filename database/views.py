from django.db.models import DateField, ExpressionWrapper, F, Max
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from database.permissions import IsAdminOrAuthenticatedAndSafeMethod
from database.serializers import *
from database.services.bulk_data_services.export_services.export_all import ExportAll
from database.services.bulk_data_services.export_services.export_instruments import ExportInstrumentsService
from database.services.bulk_data_services.export_services.export_models import ExportModelsService
from database.services.bulk_data_services.import_services.import_instruments import ImportInstrumentsService
from database.services.bulk_data_services.import_services.import_models import ImportModelsService


class ModelCategoryViewSet(viewsets.ModelViewSet):
    queryset = ModelCategory.objects.all()
    serializer_class = ModelCategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = [CategoryEnum.NAME.value]
    search_fields = [CategoryEnum.NAME.value]
    ordering_fields = [CategoryEnum.NAME.value]

    @action(detail=False, methods=['get'])
    def all(self, request):
        return Response(ModelCategorySerializer(self.queryset, many=True).data)


class EquipmentModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = EquipmentModel.objects.all()
    permission_classes = [IsAdminOrAuthenticatedAndSafeMethod]
    filterset_fields = [
        EquipmentModelEnum.VENDOR.value,
        EquipmentModelEnum.MODEL_NUMBER.value,
        EquipmentModelEnum.DESCRIPTION.value
    ]
    search_fields = [
        EquipmentModelEnum.VENDOR.value,
        EquipmentModelEnum.MODEL_NUMBER.value,
        EquipmentModelEnum.DESCRIPTION.value
    ]
    ordering_fields = [
        EquipmentModelEnum.VENDOR.value,
        EquipmentModelEnum.MODEL_NUMBER.value,
        EquipmentModelEnum.DESCRIPTION.value,
        EquipmentModelEnum.CALIBRATION_FREQUENCY.value
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
    API endpoint to get a list of vendors matching query
    """
    serializer_class = VendorAutocompleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('vendor') is not None:
            return EquipmentModel.objects.filter(vendor__contains=self.request.query_params.get('vendor'))
        return EquipmentModel.objects.all()

    def list(self, request, **kwargs):
        vendor_list = list({model.vendor for model in self.get_queryset()})
        vendor_list.sort()
        return Response(vendor_list)


class ModelAutocompleteViewSet(generics.ListAPIView):
    """
    API endpoint to get a list of models matching query
    """
    serializer_class = ModelAutocompleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = EquipmentModel.objects.all()
        if self.request.query_params.get('vendor') is not None:
            qs = qs.filter(vendor__contains=self.request.query_params.get('vendor'))
            if self.request.query_params.get('model_number') is not None:
                return qs.filter(model_number__contains=self.request.query_params.get('model_number'))
        return qs

    def list(self, request, **kwargs):
        model_list = list({model.model_number for model in self.get_queryset()})
        return Response(model_list)


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    permission_classes = [IsAdminOrAuthenticatedAndSafeMethod]
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
        InstrumentEnum.SERIAL_NUMBER.value,
        'most_recent_calibration_date',
        'calibration_expiration_date'
    ]
    ordering = ['model__vendor', 'model__model_number', 'serial_number']

    def get_queryset(self):
        mrc = Max('calibration_history__date')
        cf = F('model__calibration_frequency')
        expiration = ExpressionWrapper(mrc + cf, output_field=DateField())
        return Instrument.objects.annotate(most_recent_calibration_date=mrc).annotate(
            calibration_expiration_date=expiration)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InstrumentRetrieveSerializer  # 2.2.4
        return InstrumentSerializer  # 2.2.3

    @action(detail=False, methods=['get'])
    def all(self, request):
        return Response(InstrumentSerializer(self.get_queryset(), many=True).data)


class CalibrationEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = CalibrationEvent.objects.all()
    serializer_class = CalibrationEventSerializer
    permission_classes = [IsAdminOrAuthenticatedAndSafeMethod]
    filter_backends = []

    @action(detail=False, methods=['get'])
    def all(self, request):
        return Response(InstrumentSerializer(self.queryset, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_models(request):
    return ExportModelsService().execute()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_instruments(request):
    return ExportInstrumentsService().execute()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export(request):
    return ExportAll().execute()


@api_view(['POST'])
@permission_classes([IsAdminUser])
def import_models(request):
    return ImportModelsService(request.FILES['file'].file).execute()


@api_view(['POST'])
@permission_classes([IsAdminUser])
def import_instruments(request):
    return ImportInstrumentsService(request.FILES['file'].file).execute()
