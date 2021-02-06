from django.utils.timezone import localtime, now

from database.models import User, Model, Instrument, CalibrationEvent
from database.services.instrument_services.create_instrument import CreateInstrument
OVERLONG_STRING = "STRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRING" \
                  "STRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRING" \
                  "STRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRING" \
                  "STRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRING" \
                  "STRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRINGSTRING"

def create_admin_and_model_and_instrument():
    user, model = create_admin_and_model()
    instrument = CreateInstrument(user_id=user.id, password=user.password, model_id=model.id, serial_number="serial_number").execute()
    return user, model, instrument

def create_admin():
    return User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                               admin=True)

def create_admin_and_model():
    user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                               admin=True)
    model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
    return user, model


def create_non_admin_user():
    return User.objects.create(username="username2", password="password", name="name", email="user@gmail.com",
                               admin=False)

def create_calibration_events():
    user = create_non_admin_user()
    model = Model.objects.create(vendor="vendor", model_number="model_number", description="description",
                         comment="comment", calibration_frequency=1)
    instrument = Instrument.objects.create(model=model, serial_number="serial_number")
    earlier = localtime(now()).date()
    later = localtime(now()).date().replace(month=earlier.month + 1)
    latest = localtime(now()).date().replace(month=earlier.month + 2)
    calibration_event3 = CalibrationEvent.objects.create(instrument=instrument, user=user, date=latest)
    calibration_event = CalibrationEvent.objects.create(instrument=instrument, user=user, date=earlier)
    calibration_event2 = CalibrationEvent.objects.create(instrument=instrument, user=user, date=later)
    return calibration_event, calibration_event2, calibration_event3, user


