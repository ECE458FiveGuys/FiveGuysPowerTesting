import csv
import io
from datetime import timedelta

from django.core.exceptions import ValidationError
from rest_framework.response import Response

from database.models.model import Model
from database.serializers.model import ModelListSerializer
from database.services.table_enums import InstrumentTableColumnNames as ITCN, ModelTableColumnNames as MTCN


class ImportModels(object):

    def __init__(self, file):
        f = io.TextIOWrapper(file, encoding="utf-8-sig")
        self.reader = csv.DictReader(f)

    def bulk_import(self):
        successful_imports = []
        try:
            if set(self.reader.fieldnames) != set([e.value for e in MTCN]):
                print(self.reader.fieldnames)
                raise ValidationError("Column headers are incorrect")
            for row in self.reader:
                m = Model.objects.create(
                    vendor=self.parse_field(row, MTCN.VENDOR.value),
                    model_number=self.parse_field(row, MTCN.MODEL_NUMBER.value),
                    description=self.parse_field(row, MTCN.DESCRIPTION.value),
                    comment=self.parse_field(row, MTCN.COMMENT.value),
                    model_categories=self.parse_categories(row),
                    calibration_frequency=self.parse_calibration_frequency(row),
                    calibration_mode=self.parse_calibration_mode(row))
                successful_imports.append(m)
            return Response(status=200, data=ModelListSerializer(successful_imports, many=True).data)
        except ValidationError as e:
            for obj in successful_imports:
                obj.delete()
            return Response(status=400, data=e.messages)

    @staticmethod
    def is_comment_field(key):
        return key == MTCN.COMMENT.value or key == ITCN.COMMENT.value

    def parse_field(self, row, key):
        if not self.is_comment_field(key) and row[key].find("\n") != -1:
            raise ValidationError(f"Illegal newline character found in row {self.reader.line_num - 1} of column {key}")
        return row[key]

    def parse_categories(self, row):
        value = self.parse_field(row, MTCN.MODEL_CATEGORIES.value)
        return value.split()

    def parse_calibration_frequency(self, row):
        value = self.parse_field(row, MTCN.CALIBRATION_FREQUENCY.value)
        if value == 'N/A':
            return timedelta(days=0)
        return timedelta(days=int(value))

    def parse_calibration_mode(self, row):
        value = self.parse_field(row, MTCN.LOAD_BANK_SUPPORT.value)
        if value == 'Y':
            return 'LOAD_BANK'
        return 'DEFAULT'
