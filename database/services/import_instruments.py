import csv
from datetime import datetime

from rest_framework.response import Response

from database.models.instrument import Instrument
from database.serializers.instrument import InstrumentListSerializer
from database.services.table_enums import InstrumentTableColumnNames as ITCN, ModelTableColumnNames as MTCN
from ..exceptions import IllegalCharacterException


class ImportInstruments(object):

    def __init__(self, file):
        self.file = file
        self.asset_tags = iter(set(range(10 ** 5, 10 ** 6)) - set(Instrument.objects.asset_tag_numbers()))

    def bulk_import(self, user=None):
        successful_imports = []
        reader = csv.DictReader(self.file)
        for row in reader:
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
        return Response(status=200, data=InstrumentListSerializer(successful_imports, many=True).data)

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
        if value is None:
            return next(self.asset_tags)
        return value

    def parse_date(self, row):
        value = self.parse_field(row, ITCN.CALIBRATION_DATE.value)
        return datetime.strptime(value, '%m/%d/%Y').date()
