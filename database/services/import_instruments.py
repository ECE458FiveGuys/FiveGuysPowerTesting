import csv
from datetime import datetime

from database.models.instrument import Instrument
from database.services.import_service import ImportService
from database.services.table_enums import ModelTableColumnNames as MTCN


class ImportInstruments(ImportService):

    def __init__(self, file, column_enum, serializer, user):
        super(ImportInstruments, self).__init__(file, column_enum, serializer)
        self.user = user
        self.asset_tags = self.generate_asset_tag_numbers(self.f)
        self.f.seek(0)

    def generate_asset_tag_numbers(self, file):
        reader = csv.DictReader(file)
        a = []
        for row in reader:
            value = self.parse_field(row, self.column_enum.ASSET_TAG_NUMBER.value)
            if value != '':
                a.append(int(value))
        asset_tag_numbers = set(range(10 ** 5, 10 ** 6)) - set(Instrument.objects.asset_tag_numbers()) - set(a)
        return iter(asset_tag_numbers)

    def create_object(self, row):
        return Instrument.objects.create_for_import(
            vendor=self.parse_field(row, MTCN.VENDOR.value),
            model_number=self.parse_field(row, MTCN.MODEL_NUMBER.value),
            serial_number=self.parse_serial_number(row),
            asset_tag_number=self.parse_asset_tag_numbers(row),
            comment=self.parse_field(row, MTCN.COMMENT.value),
            instrument_categories=self.parse_categories(row),
            user=self.user,
            calibration_date=self.parse_date(row),
            calibration_comment=self.parse_field(row, self.column_enum.CALIBRATION_COMMENT.value))

    def parse_serial_number(self, row):
        value = self.parse_field(row, self.column_enum.SERIAL_NUMBER.value)
        if value == '':
            return None
        return value

    def parse_categories(self, row):
        value = self.parse_field(row, self.column_enum.INSTRUMENT_CATEGORIES.value)
        return value.split()

    def parse_asset_tag_numbers(self, row):
        value = self.parse_field(row, self.column_enum.ASSET_TAG_NUMBER.value)
        if value == '':
            return next(self.asset_tags)
        return value

    def parse_date(self, row):
        value = self.parse_field(row, self.column_enum.CALIBRATION_DATE.value)
        if value == '':
            return None
        return datetime.strptime(value, '%m/%d/%Y').date()
