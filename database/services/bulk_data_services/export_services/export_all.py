import csv
import os
import shutil
import tempfile
from io import BytesIO
from zipfile import ZipFile

from django.http import HttpResponse

from database.services.bulk_data_services.export_services.export_utils import write_instrument_file, write_model_file
# file name of folder inside zip:
from database.services.service import Service

zip_subdir = "inventory"
# file name of outer zip folder:
zip_filename = "%s.zip" % zip_subdir


class ExportAll(Service):

    def __init__(self):
        super().__init__()

    def execute(self):
        s = BytesIO()
        # make a temporary directory in which to build csv files pre-zip:
        tmp_dir = tempfile.mkdtemp()
        # create zipfile object:
        zf = ZipFile(s, 'w')
        self.add_spreadsheet_to_zip(sprdsheet_file_name="models.csv",
                                    zip_file=zf,
                                    write_function=write_model_file,
                                    tmp_dir=tmp_dir)
        self.add_spreadsheet_to_zip(sprdsheet_file_name="instruments.csv",
                                    zip_file=zf,
                                    write_function=write_instrument_file,
                                    tmp_dir=tmp_dir)

        zf.close()
        shutil.rmtree(tmp_dir)
        response = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return response

    def add_spreadsheet_to_zip(self, sprdsheet_file_name, zip_file, write_function, tmp_dir):
        file_path = os.path.join(tmp_dir, sprdsheet_file_name)
        with open(file_path, "w+", newline="") as file:
            writer = csv.writer(file)
            write_function(writer)
            file.seek(0)
            zip_path = os.path.join(zip_subdir, sprdsheet_file_name)
            zip_file.write(file_path, zip_path)
