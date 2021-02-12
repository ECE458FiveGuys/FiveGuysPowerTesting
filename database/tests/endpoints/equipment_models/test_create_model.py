from django.test import TestCase
from rest_framework.test import force_authenticate

from database.models import EquipmentModel
from database.tests.test_utils import EndpointTestCase
from database.views import EquipmentModelViewSet


class CreateModelTestCase(EndpointTestCase):

    def test_create_model_happy_case(self):
        request = self.factory.put(self.Endpoints.MODELS, {'vendor': 'vendor',
                                                           'model_number': 'model_number',
                                                           'description': 'description'})
        force_authenticate(request, self.admin)
        view = EquipmentModelViewSet.as_view({'put': 'create'})
        response = view(request)
        if response.status_code == 200:
            self.fail("model could not be created")
        model = EquipmentModel.objects.get(vendor="vendor")
        if model.vendor != 'vendor' \
            or model.model_number != 'model_number' \
            or model.description != "description":
            self.fail("created model not found")


    def test_create_model_required_(self):
        request = self.factory.put(self.Endpoints.MODELS, {})
        force_authenticate(request, self.admin)
        view = EquipmentModelViewSet.as_view({'put': 'create'})
        response = view(request)
        if response.data['vendor'][0] != "This field is required." \
                or response.data['model_number'][0] != "This field is required." \
                or response.data['description'][0] != "This field is required.":
            self.fail("model created without required fields")

    # def test_create_model_non_calib_happy_case(self):
    #     user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
    #                                admin=True)
    #     model = CreateModel(user_id=user.id, password=user.password, vendor="vendor", model_number="model_number",
    #                         description="description", calibration_frequency="NA") \
    #         .execute()
    #     models = SelectModels(user_id=user.id, password=user.password, model_id=model.id) \
    #         .execute()
    #     if models.count() != 1 or models.get(id=model.id).calibration_frequency is not None:
    #         self.fail("selected wrong models")
    #
    #
    # def test_create_model_non_unique_throws_exception(self):
    #     user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
    #                                admin=True)
    #     Model.objects.create(vendor="vendor", model_number="model_number", description="description")
    #     try:
    #         CreateModel(user_id=user.id, password=user.password, vendor="vendor", model_number="model_number",
    #                     description="description").execute()
    #         self.fail("non unqiue model was created")
    #     except FieldCombinationNotUniqueException as e:
    #         if e.message != "The combination of vendor and model_number must be unique for model":
    #             self.fail("incorrect error message thrown: {}".format(e.message))
    #         pass
    #
    # def test_create_model_not_admin_throws_exception(self):
    #     user = create_non_admin_user()
    #     try:
    #         CreateModel(user_id=user.id, password=user.password, vendor="vendor", model_number="model_number",
    #                     description="description").execute()
    #         self.fail("non admin permitted to use function")
    #     except IllegalAccessException:
    #         pass
    #
    # # Field length tests:
    #
    # def test_overlong_vendor(self):
    #     user = create_admin()
    #     try:
    #         CreateModel(user_id=user.id, password=user.password, vendor=OVERLONG_STRING,
    #                     model_number="model_number", comment="comment", description="desc",
    #                     calibration_frequency=1).execute()
    #         self.fail("overlong vendor allowed")
    #     except FieldLengthException:
    #         pass
    #
    # def test_overlong_model_number(self):
    #     user = create_admin()
    #     try:
    #         CreateModel(user_id=user.id, password=user.password, vendor="vendor",
    #                     model_number=OVERLONG_STRING, comment="comment", description="desc",
    #                     calibration_frequency=1).execute()
    #         self.fail("overlong model_num allowed")
    #     except FieldLengthException:
    #         pass
    #
    # def test_overlong_comment(self):
    #     user = create_admin()
    #     try:
    #         CreateModel(user_id=user.id, password=user.password, vendor="vendor",
    #                     model_number="model_number", comment=OVERLONG_STRING, description="desc",
    #                     calibration_frequency=1).execute()
    #         self.fail("overlong comment allowed")
    #     except FieldLengthException:
    #         pass
    #
    # def test_overlong_description(self):
    #     user = create_admin()
    #     try:
    #         CreateModel(user_id=user.id, password=user.password, vendor="vendor",
    #                     model_number="model_number", comment="comment", description=OVERLONG_STRING,
    #                     calibration_frequency=1).execute()
    #         self.fail("overlong description allowed")
    #     except FieldLengthException:
    #         pass
