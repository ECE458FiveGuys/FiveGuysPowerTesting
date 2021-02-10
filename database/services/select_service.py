import abc
from tkinter import ALL

from django.core.paginator import Paginator
from django.db.models import Q

from database.services.in_app_service import InAppService


class SelectService(InAppService):

    ALL = "ALL"

    def __init__(self, user_id, password, admin_only, order_by=None, num_per_page=ALL):
        self.order_by = order_by
        self.num_per_page = num_per_page
        super().__init__(user_id, password, admin_only)

    def execute(self):
        output = self.filter_by_fields()
        return self.sort_output(output)

    @abc.abstractmethod
    def filter_by_fields(self):
        pass

    def sort_output(self, output):
        if self.order_by is not None:
            output = output.order_by(self.order_by)
        if self.num_per_page != SelectService.ALL:
            return Paginator(output, self.num_per_page)
        return output

    def add_to_query(self, term, query=None, operation=Q.AND):
        if query is None:
            query = term
        else:
            query.add(term, operation)
        return query
