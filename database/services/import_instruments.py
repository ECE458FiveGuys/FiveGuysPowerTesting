import csv
from datetime import datetime
from io import StringIO

from django.core.exceptions import ValidationError
from rest_framework.response import Response

from database.models.instrument import Instrument
from database.serializers.instrument import InstrumentBulkImportSerializer
from database.services.table_enums import InstrumentTableColumnNames as ITCN, ModelTableColumnNames as MTCN
from ..exceptions import IllegalCharacterException


class ImportInstruments(object):

    def __init__(self, file):
        decoded_file = file.read().decode('utf-8-sig')
        self.file = StringIO(decoded_file)
        self.reader = csv.DictReader(self.file)
        self.asset_tags = self.generate_asset_tag_numbers(file)

    def generate_asset_tag_numbers(self, file):
        file.seek(0)
        decoded_file = file.read().decode('utf-8-sig')
        reader = csv.DictReader(StringIO(decoded_file))
        a = []
        for row in reader:
            value = self.parse_field(row, ITCN.ASSET_TAG_NUMBER.value)
            if value != '':
                a.append(int(value))
        asset_tag_numbers = set(range(10 ** 5, 10 ** 6)) - set(Instrument.objects.asset_tag_numbers()) - set(a)
        return iter(asset_tag_numbers)

    def bulk_import(self, user=None):
        successful_imports = []
        try:
            for row in self.reader:
                m = Instrument.objects.create_for_import(
                    vendor=self.parse_field(row, MTCN.VENDOR.value),
                    model_number=self.parse_field(row, MTCN.MODEL_NUMBER.value),
                    serial_number=self.parse_field(row, ITCN.SERIAL_NUMBER.value),
                    asset_tag_number=self.parse_asset_tag_numbers(row),
                    comment=self.parse_field(row, MTCN.COMMENT.value),
                    instrument_categories=self.parse_categories(row),
                    user=user,
                    calibration_date=self.parse_date(row),
                    calibration_comment=self.parse_field(row, ITCN.CALIBRATION_COMMENT.value))
                successful_imports.append(m)
            return Response(status=200, data=InstrumentBulkImportSerializer(successful_imports, many=True).data)
        except ValidationError as e:
            for obj in successful_imports:
                obj.delete()
            return Response(status=400, data=e.messages)

    @staticmethod
    def is_comment_field(key):
        return key == MTCN.COMMENT.value or key == ITCN.COMMENT.value

    def parse_field(self, row, key):
        if not self.is_comment_field(key) and row[key].find("\n") != -1:
            raise IllegalCharacterException(key)
        return row[key]

    def parse_categories(self, row):
        value = self.parse_field(row, ITCN.INSTRUMENT_CATEGORIES.value)
        return value.split()

    def parse_asset_tag_numbers(self, row):
        value = self.parse_field(row, ITCN.ASSET_TAG_NUMBER.value)
        if value == '':
            return next(self.asset_tags)
        return value

    def parse_date(self, row):
        value = self.parse_field(row, ITCN.CALIBRATION_DATE.value)
        if value == '':
            return None
        return datetime.strptime(value, '%m/%d/%Y').date()
