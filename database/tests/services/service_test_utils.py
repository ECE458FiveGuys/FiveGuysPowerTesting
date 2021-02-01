from database.models import User, Model
from database.services.instrument_services.create_instrument import CreateInstrument


def create_admin_and_model_and_instrument():
    user, model = create_admin_and_model()
    instrument = CreateInstrument(user=user, model_id=model.id, serial_number="serial_number").execute()
    return user, model, instrument


def create_admin_and_model():
    user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                               admin=True)
    model = Model.objects.create(vendor="vendor", model_number="model_number", description="description")
    return user, model


def create_non_admin_user():
    return User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                               admin=False)
