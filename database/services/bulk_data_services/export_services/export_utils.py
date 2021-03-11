from datetime import timedelta

from database.models.instrument import CalibrationEvent
from database.services.table_enums import MaxInstrumentTableColumnNames, ModelTableColumnNames


def write_instrument_file(writer, queryset):
    instruments = queryset
    writer.writerow([e.value for e in MaxInstrumentTableColumnNames])
    for instrument in instruments:
        latest_calibration_event = CalibrationEvent.objects \
            .filter(instrument=instrument) \
            .order_by("-date") \
            .first()
        writer.writerow([instrument.model.vendor,
                         instrument.model.model_number,
                         instrument.serial_number,
                         instrument.asset_tag_number,
                         instrument.comment,
                         None if latest_calibration_event is None else "{}/{}/{}"
                        .format(latest_calibration_event.date.month,
                                latest_calibration_event.date.day,
                                latest_calibration_event.date.year),
                         None if latest_calibration_event is None else latest_calibration_event.comment,
                         ' '.join([mc.__str__() for mc in instrument.instrument_categories.all()]),
                         None if latest_calibration_event is None else latest_calibration_event.additional_evidence,
                         None if latest_calibration_event is None else None if latest_calibration_event.load_bank_data == "" else "Y"])


def write_model_file(writer, queryset):
    models = queryset
    writer.writerow([e.value for e in ModelTableColumnNames])
    for model in models:
        writer.writerow([model.vendor,
                         model.model_number,
                         model.description,
                         model.comment,
                         ' '.join([mc.__str__() for mc in model.model_categories.all()]),
                         "Y" if model.calibration_mode == "LOAD_BANK" else "",
                         "N/A" if model.calibration_frequency == timedelta(
                             days=0) else model.calibration_frequency.days])
