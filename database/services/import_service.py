import csv
import io
from abc import ABC, abstractmethod

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.response import Response

from database.exceptions import DuplicateObjectError, IllegalColumnHeadersError, IllegalNewlineCharacterError, \
    ModelDoesNotExistError, \
    SpecificValidationError
from database.services.table_enums import ModelTableColumnNames as MTCN


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
                m = self.create(row)
                successful_imports.append(m)
            return Response(status=200, data=self.serializer(successful_imports, many=True).data)
        except ValidationError as e:
            for obj in successful_imports:
                obj.delete()
            return Response(status=400, data=e.messages)

    def create(self, row):
        try:
            return self.create_object(row)
        except ObjectDoesNotExist:
            raise ModelDoesNotExistError(self.reader.line_num, row[MTCN.VENDOR.value], row[MTCN.MODEL_NUMBER.value])
        except ValidationError as v:
            try:
                key = list(v.message_dict.keys())[0]
                value = v.message_dict[key][0]
                if key in [e.value.lower().replace('-', '_') for e in self.min_column_enum]:
                    raise SpecificValidationError(self.reader.line_num, key.title().replace('_', '-'), value)
                else:
                    raise DuplicateObjectError(self.reader.line_num, value)
            except AttributeError:
                raise v

    @abstractmethod
    def create_object(self, row):
        return NotImplemented

    def is_comment_field(self, key):
        return key == self.min_column_enum.COMMENT.value

    def parse_field(self, row, key):
        if not self.is_comment_field(key) and row[key].find("\n") != -1:
            raise IllegalNewlineCharacterError(row=self.reader.line_num - 1, col=key)
        return row[key]
