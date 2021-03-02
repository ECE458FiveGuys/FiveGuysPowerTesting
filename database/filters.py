"""
Base code from https://www.django-rest-framework.org/api-guide/filtering/
"""
from django_filters import rest_framework as rf
from rest_framework import filters

from database.model_enums import InstrumentEnum, ModelEnum
from database.models.instrument import Instrument
from database.models.model import Model


class CustomSearchFilter(filters.SearchFilter):
    """
    Implementation of search that allows for keyword search on one specific field as opposed to all of the fields listed
    in the search_fields variable of a ModelView. Discussed with Diego Chamorro
    """

    def get_search_fields(self, view, request):
        search_fields = super(CustomSearchFilter, self).get_search_fields(view, request)  # get possible search fields
        if "search_field" in request.query_params:  # check if doing a search on single field
            field = request.query_params.get("search_field")  # get field attempting to search on
            if field in search_fields:  # check if field is valid
                return [field]
        return search_fields


class CategoryFilter(rf.Filter):
    """
    Allows for searching multiple categories at once.

    Usage:
        GET https://group_six_prod.colab.duke.edu/models/?model_categories__name=multimeter,ammeter/

    In short, parameter can have a single key with multiple comma separated values.

    Usage of self.lookup_expr adapted from code from django_filters/filters.py. Discussed with Diego Chamorro.
    """

    def filter(self, qs, value):
        if value:
            for v in value.split(','):
                qs = qs.filter(**{self.field_name + '__' + self.lookup_expr: v})
        return qs


class ModelFilter(rf.FilterSet):
    """
    Requirement 2.1.3.2: It should be possible to filter this view by keyword search on the fields of vendor,
    model number, and short description. The view should also be filterable by an easily selected set of model
    categories; items shown must have all selected categories.
    """
    model_categories__name = CategoryFilter(field_name='model_categories__name', lookup_expr='exact')

    class Meta:
        model = Model
        fields = [
            ModelEnum.VENDOR.value,
            ModelEnum.MODEL_NUMBER.value,
            ModelEnum.DESCRIPTION.value,
            'model_categories__name',
        ]


class InstrumentFilter(rf.FilterSet):
    """
    Requirement 2.2.3.2: It should be possible to filter this view by keyword search on the fields of vendor,
    model number, short description, serial number, asset tag. The view should also be filterable by an easily
    selected set of categories (both model and instrument); items shown must have all selected categories.
    """
    instrument_categories__name = CategoryFilter(field_name='instrument_categories__name', lookup_expr='exact')
    model__model_categories__name = CategoryFilter(field_name='model__model_categories__name', lookup_expr='exact')

    class Meta:
        """
        Bug: Causing Error where InstrumentManager may no longer filter queryset by field calibration_history because
        it is not a field in the Instrument model (it is a related_name in ForeignKey field in CalibrationHistory)

        Solution: Moved get_queryset() to InstrumentViewSet
        """
        model = Instrument
        fields = [
            'model__' + ModelEnum.VENDOR.value,
            'model__' + ModelEnum.MODEL_NUMBER.value,
            'model__' + ModelEnum.DESCRIPTION.value,
            'model__model_categories__name',
            InstrumentEnum.SERIAL_NUMBER.value,
            'instrument_categories__name',
            InstrumentEnum.ASSET_TAG_NUMBER.value,
        ]
