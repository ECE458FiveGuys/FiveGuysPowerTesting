import abc
import csv
import io

from rest_framework import status
from rest_framework.response import Response

from database.exceptions import IllegalCharacterException, UserError
from database.services.bulk_data_services.table_enums import InstrumentTableColumnNames, ModelTableColumnNames
from database.services.service import Service


class ImportService(Service):

    def __init__(self, import_file, fields):
        self.file = import_file
        self.fields = fields

    def execute(self):
        created_objects = []
        objects_to_return = []
        try:
            param_file = io.TextIOWrapper(self.file, encoding="utf-8")
            reader = csv.DictReader(param_file)
            if set(reader.fieldnames) != set(self.fields):
                raise UserError("Column headers incorrect")
            list_of_dict = list(reader)
            for row in list_of_dict:
                if all(row[field] == '' for field in self.fields):  # if all elements in row are empty, skip
                    continue
                objects = self.create_objects_from_row(row)  # returns all objects created
                created_objects += objects
                objects_to_return.append(objects[0])  # first object returned is the type to be serialized and returned
            return Response(self.serialize(objects_to_return).data)
        except UserError as e:
            self.undo_object_creations(created_objects)
            return Response(e.message, status=status.HTTP_400_BAD_REQUEST, content_type="utf-8")

    def undo_object_creations(self, created_objects):
        for obj in created_objects:
            obj.delete()

    def parse_field(self, row, key):
        if key != ModelTableColumnNames.COMMENT.value \
                and key != InstrumentTableColumnNames.COMMENT.value \
                and row[key].find("\n") != -1:
            raise IllegalCharacterException(key)
        return None if row[key] == '' else row[key]

    @abc.abstractmethod
    def create_objects_from_row(self, row):
        pass

    @abc.abstractmethod
    def serialize(self, created_objects):
        pass
