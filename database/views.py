import importlib

from django.db.models import DateField, ExpressionWrapper, F, Max
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from database.filters import InstrumentFilter, ModelFilter
from database.models.instrument import CalibrationEvent
from database.models.instrument_category import InstrumentCategory
from database.serializers.calibration_event import CalibrationEventSerializer
from database.serializers.instrument import InstrumentBulkImportSerializer, InstrumentRetrieveSerializer, \
    InstrumentSerializer
from database.serializers.model import *
from database.services.bulk_data_services.export_services.export_instruments import ExportInstrumentsService
from database.services.bulk_data_services.export_services.export_models import ExportModelsService
from database.services.import_instruments import ImportInstruments
from database.services.import_models import ImportModels
from database.services.table_enums import MaxInstrumentTableColumnNames, MinInstrumentTableColumnNames, \
    ModelTableColumnNames


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CategoryViewSet(viewsets.ModelViewSet):
    filterset_fields = [CategoryEnum.NAME.value]
    search_fields = [CategoryEnum.NAME.value]
    ordering_fields = [CategoryEnum.NAME.value]

    def get_serializer_class(self):
        name = self.__class__.__name__.replace('ViewSet', '')
        model = name.replace('Category', '').lower()
        m = importlib.import_module(f'database.serializers.{model}')
        if self.action == 'retrieve':
            return getattr(m, f'{name}RetrieveSerializer')
        return getattr(m, f'{name}Serializer')


class ModelCategoryViewSet(CategoryViewSet):
    queryset = ModelCategory.objects.all()


class InstrumentCategoryViewSet(CategoryViewSet):
    queryset = InstrumentCategory.objects.all()


class ModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Model.objects.all()
    filterset_class = ModelFilter
    pagination_class = SmallResultsSetPagination
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
            return ModelRetrieveSerializer
        return ModelSerializer

    @action(['get'], detail=False)
    def vendors(self, request):
        model_number = request.query_params.get('model_number')
        return Response(Model.objects.vendors(model_number))

    @action(['get'], detail=False)
    def model_numbers(self, request):
        vendor = request.query_params.get('vendor')
        return Response(Model.objects.model_numbers(vendor=vendor))

    @action(['get'], detail=False)
    def export(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return ExportModelsService().execute(queryset)

    @action(['get'], detail=False)
    def all(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        return Response(serializer(self.get_queryset(), many=True).data)


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows instruments to be viewed or edited.
    """
    queryset = Instrument.objects.all()
    filterset_class = InstrumentFilter
    pagination_class = SmallResultsSetPagination
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

    @action(['get'], detail=False)
    def calibratable_asset_tag_numbers(self, request, *args, **kwargs):
        return Response(Instrument.objects.calibratable_asset_tag_numbers())

    @action(['get'], detail=False)
    def export(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return ExportInstrumentsService().execute(queryset)

    @action(['get'], detail=False)
    def all(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        return Response(serializer(self.get_queryset(), many=True).data)

    @action(['get'], detail=False)
    def asset_tag_numbers(self, request, *args, **kwargs):
        pks = request.data.get('pks')
        return Response(Instrument.objects.asset_tag_numbers(pks))


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


class ModelUploadView(APIView):
    parser_classes = [MultiPartParser, ]
    permission_classes = [IsAdminUser]

    def post(self, request):
        file = request.data['file']
        return ImportModels(file, ModelListSerializer, ModelTableColumnNames).bulk_import()


class InstrumentUploadView(APIView):
    parser_classes = [MultiPartParser, ]
    permission_classes = [IsAdminUser]

    def post(self, request):
        file = request.data['file']
        return ImportInstruments(file, InstrumentBulkImportSerializer, MinInstrumentTableColumnNames,
                                 MaxInstrumentTableColumnNames, self.request.user).bulk_import()
