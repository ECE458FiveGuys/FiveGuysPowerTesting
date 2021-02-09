from django.test import TestCase

from database.exceptions import RequiredFieldsEmptyException, FieldCombinationNotUniqueException, \
    IllegalAccessException, FieldLengthException
from database.models import Model, User
from database.services.model_services.create_model import CreateModel
from database.services.model_services.select_models import SelectModels
from database.tests.services.service_test_utils import create_non_admin_user, create_admin, OVERLONG_STRING


class CreateModelTestCase(TestCase):

    def test_create_model_happy_case(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        model = CreateModel(user_id=user.id, password=user.password, vendor="vendor", model_number="model_number", description="description")\
            .execute()
        models = SelectModels(user_id=user.id, password=user.password, model_id=model.id)\
            .execute()
        if models.count() != 1 or models.get(id=model.id) != model:
            self.fail("selected wrong models")

    def test_create_model_non_calib_happy_case(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        model = CreateModel(user_id=user.id, password=user.password, vendor="vendor", model_number="model_number", description="description", calibration_frequency="NA")\
            .execute()
        models = SelectModels(user_id=user.id, password=user.password, model_id=model.id)\
            .execute()
        if models.count() != 1 or models.get(id=model.id).calibration_frequency is not None:
            self.fail("selected wrong models")

    def test_create_model_without_required_fields_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        try:
            CreateModel(user_id=user.id, password=user.password, vendor=None, model_number=None, description=None).execute()
            self.fail("model without required fields was created")
        except RequiredFieldsEmptyException as e:
            if e.message != "vendor and model_number and description are required fields for the model with vendor 'None' and model number 'None'":
                message = "incorrect error message thrown: {}".format(e.message)
                self.fail(message)
            pass

    def test_create_model_non_unique_throws_exception(self):
        user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
                                   admin=True)
        Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        try:
            CreateModel(user_id=user.id, password=user.password, vendor="vendor", model_number="model_number", description="description").execute()
            self.fail("non unqiue model was created")
        except FieldCombinationNotUniqueException as e:
            if e.message != "The combination of vendor and model_number must be unique for the model with vendor 'vendor' and model number 'model_number'":
                self.fail("incorrect error message thrown: {}".format(e.message))
            pass

    def test_create_model_not_admin_throws_exception(self):
        user = create_non_admin_user()
        try:
            CreateModel(user_id=user.id, password=user.password, vendor="vendor", model_number="model_number", description="description").execute()
            self.fail("non admin permitted to use function")
        except IllegalAccessException:
            pass

    # Field length tests:

    def test_overlong_vendor(self):
        user = create_admin()
        try:
            CreateModel(user_id=user.id, password=user.password, vendor=OVERLONG_STRING,
                                 model_number="model_number", comment="comment", description="desc",
                                 calibration_frequency=1).execute()
            self.fail("overlong vendor allowed")
        except FieldLengthException:
            pass


    def test_overlong_model_number(self):
        user = create_admin()
        try:
            CreateModel(user_id=user.id, password=user.password, vendor="vendor",
                                 model_number=OVERLONG_STRING, comment="comment", description="desc",
                                 calibration_frequency=1).execute()
            self.fail("overlong model_num allowed")
        except FieldLengthException:
            pass

    def test_overlong_comment(self):
        user = create_admin()
        try:
            CreateModel(user_id=user.id, password=user.password, vendor="vendor",
                                 model_number="model_number", comment=OVERLONG_STRING, description="desc",
                                 calibration_frequency=1).execute()
            self.fail("overlong comment allowed")
        except FieldLengthException:
            pass

    def test_overlong_description(self):
        user = create_admin()
        try:
            CreateModel(user_id=user.id, password=user.password, vendor="vendor",
                                 model_number="model_number", comment="comment", description=OVERLONG_STRING,
                                 calibration_frequency=1).execute()
            self.fail("overlong description allowed")
        except FieldLengthException:
            pass