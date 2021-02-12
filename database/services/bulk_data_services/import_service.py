import abc
import csv
import io

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from database.exceptions import UserError
from database.services.service import Service


class ImportService(Service):

    def __init__(self, import_file, fields):
        self.file = import_file
        self.fields = fields

    def execute(self):
        created_objects = []
        try:
            param_file = io.TextIOWrapper(self.file)
            reader = csv.DictReader(param_file)
            if set(reader.fieldnames) != set(self.fields):
                raise UserError("Column headers incorrect")
            list_of_dict = list(reader)
            for row in list_of_dict:
                if all(row[field] == '' for field in self.fields): # if all elements in row are empty, skip
                    continue
                obj = self.create_object_from_row(row)
                created_objects.append(obj)
            return Response(self.serialize(created_objects).data)
        except UserError as e:
            self.undo_object_creations(created_objects)
            return Response(e.message, status=status.HTTP_400_BAD_REQUEST)

    def undo_object_creations(self, created_objects):
        for obj in created_objects:
            obj.delete()

    def parse_field(self, row, key):
        return None if row[key] == '' else row[key]

    @abc.abstractmethod
    def create_object_from_row(self, row):
        pass

    @abc.abstractmethod
    def serialize(self, created_objects):
        pass

