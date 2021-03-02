from io import StringIO

from django.db.models import DateField, ExpressionWrapper, F, Max
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from database.filters import InstrumentFilter, ModelFilter
from database.models.calibration_event import CalibrationEvent
from database.models.instrument_category import InstrumentCategory
from database.serializers.calibration_event import CalibrationEventSerializer
from database.serializers.instrument import InstrumentCategoryRetrieveSerializer, InstrumentCategorySerializer, \
    InstrumentRetrieveSerializer, InstrumentSerializer
from database.serializers.model import *
from database.services.bulk_data_services.export_services.export_all import ExportAll
from database.services.bulk_data_services.export_services.export_instruments import ExportInstrumentsService
from database.services.bulk_data_services.export_services.export_models import ExportModelsService
from database.services.bulk_data_services.import_services.import_instruments import ImportInstrumentsService
from database.services.bulk_data_services.import_services.import_models import ImportModelsService
from database.services.import_models import ImportModels


class ModelCategoryViewSet(viewsets.ModelViewSet):
    queryset = ModelCategory.objects.all()
    serializer_class = ModelCategorySerializer
    filterset_fields = [CategoryEnum.NAME.value]
    search_fields = [CategoryEnum.NAME.value]
    ordering_fields = [CategoryEnum.NAME.value]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ModelCategoryRetrieveSerializer
        return ModelCategorySerializer


class InstrumentCategoryViewSet(viewsets.ModelViewSet):
    queryset = InstrumentCategory.objects.all()
    serializer_class = InstrumentCategorySerializer
    filterset_fields = [CategoryEnum.NAME.value]
    search_fields = [CategoryEnum.NAME.value]
    ordering_fields = [CategoryEnum.NAME.value]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InstrumentCategoryRetrieveSerializer
        return InstrumentCategorySerializer


class ModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Model.objects.all()
    filterset_class = ModelFilter
    search_fields = [
        ModelEnum.VENDOR.value,
        ModelEnum.MODEL_NUMBER.value,
        ModelEnum.DESCRIPTION.value,
        'model_categories__name',
    ]
    ordering_fields = [
        ModelEnum.VENDOR.value,
        ModelEnum.MODEL_NUMBER.value,
        ModelEnum.DESCRIPTION.value,
        ModelEnum.CALIBRATION_FREQUENCY.value,
    ]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ModelRetrieveSerializer  # 2.1.4
        return ModelSerializer  # 2.1.3

    @action(detail=False, methods=['get'])
    def vendors(self, request):
        return Response(Model.objects.vendors())

    @action(detail=False, methods=['get'])
    def model_numbers(self, request):
        vendor = request.query_params.get('vendor')
        return Response(Model.objects.models(vendor=vendor))


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Instrument.objects.all()
    filterset_class = InstrumentFilter
    search_fields = [
        'model__' + ModelEnum.VENDOR.value,
        'model__' + ModelEnum.MODEL_NUMBER.value,
        'model__' + ModelEnum.DESCRIPTION.value,
        'model__model_categories__name',
        InstrumentEnum.SERIAL_NUMBER.value,
        'instrument_categories__name',
        InstrumentEnum.ASSET_TAG_NUMBER.value,
    ]
    ordering_fields = [
        'model__' + ModelEnum.VENDOR.value,
        'model__' + ModelEnum.MODEL_NUMBER.value,
        'model__' + ModelEnum.DESCRIPTION.value,
        InstrumentEnum.SERIAL_NUMBER.value,
        'most_recent_calibration_date',
        'calibration_expiration_date',
        InstrumentEnum.ASSET_TAG_NUMBER.value,
    ]
    ordering = ['model__vendor', 'model__model_number', 'serial_number']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InstrumentRetrieveSerializer  # 2.2.4
        return InstrumentSerializer  # 2.2.3

    def get_queryset(self):
        mrc = Max('calibration_history__date')
        cf = F('model__calibration_frequency')
        expiration = ExpressionWrapper(mrc + cf, output_field=DateField())
        qs = super().get_queryset().annotate(most_recent_calibration_date=mrc)
        return qs.annotate(calibration_expiration_date=expiration)


class CalibrationEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = CalibrationEvent.objects.all()
    serializer_class = CalibrationEventSerializer
    filter_backends = []

    @action(detail=False, methods=['get'])
    def all(self, request):
        return Response(InstrumentSerializer(self.queryset, many=True).data)


class FileUploadView(APIView):
    parser_classes = [FileUploadParser]

    def put(self, request):
        file = request.data['file']
        decoded_file = file.read().decode('utf8')
        csv_file = StringIO(decoded_file)
        next(csv_file)
        next(csv_file)
        next(csv_file)
        next(csv_file)
        return ImportModels(csv_file).bulk_import()


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
