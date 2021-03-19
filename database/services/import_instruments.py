import csv
from datetime import datetime

from database.exceptions import IllegalValueError
from database.models.instrument import Instrument
from database.services.import_service import ImportService
from database.services.table_enums import ModelTableColumnNames as MTCN


class ImportInstruments(ImportService):

    def __init__(self, file, serializer, min_column_enum, max_column_enum, user):
        super(ImportInstruments, self).__init__(file, serializer, min_column_enum, max_column_enum)
        self.user = user
        self.asset_tags = self.generate_asset_tag_numbers(self.f)
        self.f.seek(0)

    def generate_asset_tag_numbers(self, file):
        reader = csv.DictReader(file)
        a = []
        try:
            for row in reader:
                value = self.parse_field(row, self.min_column_enum.ASSET_TAG_NUMBER.value)
                if value != '':
                    a.append(int(value))
            asset_tag_numbers = set(range(10 ** 5, 10 ** 6)) - set(Instrument.objects.asset_tag_numbers()) - set(a)
            return iter(asset_tag_numbers)
        except KeyError:
            return

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
            calibration_comment=self.parse_field(row, self.min_column_enum.CALIBRATION_COMMENT.value))

    def parse_serial_number(self, row):
        value = self.parse_field(row, self.min_column_enum.SERIAL_NUMBER.value)
        if value == '':
            return None
        return value

    def parse_categories(self, row):
        value = self.parse_field(row, self.min_column_enum.INSTRUMENT_CATEGORIES.value)
        return value.split()

    def parse_asset_tag_numbers(self, row):
        value = self.parse_field(row, self.min_column_enum.ASSET_TAG_NUMBER.value)
        if value == '':
            return next(self.asset_tags)
        return value

    def parse_date(self, row):
        key = self.min_column_enum.CALIBRATION_DATE.value
        value = self.parse_field(row, key)
        if value == '':
            return None
        try:
            return datetime.strptime(value, '%m/%d/%Y').astimezone()
        except ValueError:
            raise IllegalValueError(self.reader.line_num, key, "format MM/DD/YYYY", value)
