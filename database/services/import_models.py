import csv
from datetime import timedelta

from rest_framework.response import Response

from .bulk_data_services.table_enums import InstrumentTableColumnNames as ITCN, ModelTableColumnNames as MTCN
from .manager import BulkCreateManager
from ..exceptions import IllegalCharacterException
from ..models.model import Model


class ImportModels(object):

    def __init__(self, file):
        self.file = file

    def bulk_import(self):
        successful_imports = []
        bulk_mgr = BulkCreateManager()
        reader = csv.DictReader(self.file, dialect='excel')
        for row in reader:
            if row[MTCN.VENDOR.value].find('--') != -1:
                break
            print(row)
            m = Model(vendor=self.parse_field(row, MTCN.VENDOR.value),
                      model_number=self.parse_field(row, MTCN.MODEL_NUMBER.value),
                      description=self.parse_field(row, MTCN.DESCRIPTION.value),
                      comment=self.parse_field(row, MTCN.COMMENT.value),
                      calibration_frequency=timedelta(days=0) if row[MTCN.CALIBRATION_FREQUENCY.value] == 'N/A' else
                      timedelta(days=int(row[MTCN.CALIBRATION_FREQUENCY.value])),
                      calibration_mode='DEFAULT')
            bulk_mgr.add(m)
            successful_imports.append(m)
        bulk_mgr.done()
        return Response(status=200)

    @staticmethod
    def is_comment_field(key):
        return key == MTCN.COMMENT.value or key == ITCN.COMMENT.value

    def parse_field(self, row, key):
        if not self.is_comment_field(key) and row[key].find("\n") != -1:
            raise IllegalCharacterException(key)
        return row[key]
