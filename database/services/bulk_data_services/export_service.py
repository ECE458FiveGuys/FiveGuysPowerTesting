import abc
import csv

from django.http import HttpResponse

from database.services.service import Service


class ExportService(Service):

    def __init__(self, file_name):
        self.file_name = file_name

    def execute(self, queryset):
        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % self.file_name
        writer = csv.writer(response)
        self.write_file(writer, queryset=queryset)
        return response

    @abc.abstractmethod
    def write_file(self, writer, queryset):
        pass
