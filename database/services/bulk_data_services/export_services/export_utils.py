from database.models import Instrument, CalibrationEvent, EquipmentModel
from database.services.bulk_data_services.table_enums import InstrumentTableColumnNames, ModelTableColumnNames


def write_instrument_file(writer):
    instruments = Instrument.objects.all()
    writer.writerow([e.value for e in InstrumentTableColumnNames])
    for instrument in instruments:
        latest_calibration_event = CalibrationEvent.objects \
            .filter(instrument=instrument) \
            .order_by("-date") \
            .first()
        writer.writerow([instrument.model.vendor,
                         instrument.model.model_number,
                         instrument.serial_number,
                         instrument.comment,
                         None if latest_calibration_event is None else "{}/{}/{}"
                        .format(latest_calibration_event.date.month,
                                latest_calibration_event.date.day,
                                latest_calibration_event.date.year),
                         None if latest_calibration_event is None else latest_calibration_event.comment])


def write_model_file(writer):
    models = EquipmentModel.objects.all()
    writer.writerow([e.value for e in ModelTableColumnNames])
    for model in models:
        writer.writerow([model.vendor,
                         model.model_number,
                         model.description,
                         model.comment,
                         "N/A" if model.calibration_frequency is None else model.calibration_frequency])
