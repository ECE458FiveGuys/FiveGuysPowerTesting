import csv
import io
from abc import ABC, abstractmethod

from django.core.exceptions import ValidationError
from rest_framework.response import Response

from database.exceptions import IllegalColumnHeadersError, IllegalNewlineCharacterError


class ImportService(ABC):

    def __init__(self, file, serializer, min_column_enum, max_column_enum=None):
        if max_column_enum is None:
            max_column_enum = min_column_enum
        self.f = io.TextIOWrapper(file, encoding="utf-8-sig")
        self.reader = csv.DictReader(self.f)
        self.min_column_enum = min_column_enum
        self.max_column_enum = max_column_enum
        self.serializer = serializer

    def bulk_import(self):
        successful_imports = []
        try:
            if not (set(self.reader.fieldnames).issubset(set([e.value for e in self.max_column_enum]))
                    and set(self.reader.fieldnames).issuperset(set([e.value for e in self.min_column_enum]))
                    and len(self.reader.fieldnames) == len(set(self.reader.fieldnames))):
                raise IllegalColumnHeadersError(', '.join([e.value for e in self.min_column_enum]))
            for row in self.reader:
                if all(value == '' for value in row.values()):
                    continue
                m = self.create_object(row)
                successful_imports.append(m)
            return Response(status=200, data=self.serializer(successful_imports, many=True).data)
        except ValidationError as e:
            for obj in successful_imports:
                obj.delete()
            return Response(status=400, data=e.messages)

    @abstractmethod
    def create_object(self, row):
        return NotImplemented

    def is_comment_field(self, key):
        return key == self.min_column_enum.COMMENT.value

    def parse_field(self, row, key):
        if not self.is_comment_field(key) and row[key].find("\n") != -1:
            raise IllegalNewlineCharacterError(row=self.reader.line_num - 1, col=key)
        return row[key]
