"""
Base code from https://www.django-rest-framework.org/api-guide/filtering/

Discussed code to programmatically get search fields with Diego Chamorro. Original code is his.
"""
from rest_framework import filters


class CustomSearchFilter(filters.SearchFilter):
    """
    Implementation of search that allows for keyword search on one specific field as opposed to all of the fields listed
    in the search_fields variable of a ModelView.
    """
    def get_search_fields(self, view, request):
        search_fields = super(CustomSearchFilter, self).get_search_fields(view, request)  # get possible search fields
        if "search_field" in request.query_params:  # check if doing a search on single field
            field = request.query_params.get("search_field")  # get field attempting to search on
            if field in search_fields:  # check if field is valid
                return [field]
        return search_fields
