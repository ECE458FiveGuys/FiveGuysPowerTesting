from datetime import timedelta

from database.models.instrument import CalibrationEvent
from database.services.table_enums import MaxInstrumentTableColumnNames, ModelTableColumnNames


def special_file(calibration_mode, calibration_event):
    if calibration_mode == 'DEFAULT':
        return calibration_event.additional_evidence
    elif calibration_mode == 'LOAD_BANK':
        return 'Load Bank Calibration'
    elif calibration_mode == 'GUIDED_HARDWARE':
        return 'Guided Hardware Calibration'
    elif calibration_mode == 'CUSTOM':
        return 'Custom Form Calibration'
    return None


def write_instrument_file(writer, queryset):
    instruments = queryset
    writer.writerow([e.value for e in MaxInstrumentTableColumnNames])
    for instrument in instruments:
        latest_calibration_event = CalibrationEvent.objects.find_valid_calibration_event(instrument.pk)
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
                         special_file(instrument.model.calibration_mode, latest_calibration_event)])


def write_model_file(writer, queryset):
    models = queryset
    writer.writerow([e.value for e in ModelTableColumnNames])
    for model in models:
        writer.writerow(
            [
                model.vendor,
                model.model_number,
                model.description,
                model.comment,
                ' '.join([mc.__str__() for mc in model.model_categories.all()]),
                "Y" if model.calibration_mode == "LOAD_BANK" else "Klufe" if model.calibration_mode == 'GUIDED_HARDWARE' else "",
                "N/A" if model.calibration_frequency == timedelta(days=0) else model.calibration_frequency.days,
                ' '.join([mc.__str__() for mc in model.calibrator_categories.all()]),
                "Y" if model.custom_form != "" else ""
            ]
        )
