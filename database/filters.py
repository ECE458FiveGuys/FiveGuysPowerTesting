"""
Base code from https://www.django-rest-framework.org/api-guide/filtering/

Discussed code to programmatically get search fields with Diego Chamorro. Original code is his.
"""
from rest_framework import filters


class CustomSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        search_fields = super(CustomSearchFilter, self).get_search_fields(view, request)
        if "search_field" in request.query_params:
            field_to_search = request.query_params.get("search_field")
            if field_to_search in search_fields:
                return [field_to_search]
        return search_fields
