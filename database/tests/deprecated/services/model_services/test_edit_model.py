# from django.test import TestCase
#
# from database.exceptions import RequiredFieldsEmptyException, FieldCombinationNotUniqueException, \
#     IllegalAccessException, EntryDoesNotExistException
# from database.models import EquipmentModel, User
# from database.services.model_services.create_model import CreateModel
# from database.services.model_services.edit_model import EditModel
# from database.services.model_services.select_models import SelectModels
# from database.tests.services.service_test_utils import create_admin_and_model
#
#
# class EditModelTestCase(TestCase):
#
#     def test_edit_instrument_happy_case(self):
#         user, model = create_admin_and_model()
#         EditModel(user_id=user.id, password=user.password, model_id=model.id, vendor="vendor", description="description", model_number="model_number_2").execute()
#         models = SelectModels(user_id=user.id, password=user.password, model_id=model.id).execute()
#         if models.count() != 1 or models.get(id=model.id).model_number != "model_number_2":
#             self.fail("selected wrong model")
#
#     def test_edit_model_without_required_fields_throws_exception(self):
#         user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
#                                    admin=True)
#         model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description")
#         try:
#             EditModel(user_id=user.id, password=user.password, model_id=model.id, vendor=None, model_number=None, description=None).execute()
#             self.fail("model without required fields was created")
#         except RequiredFieldsEmptyException as e:
#             if e.message != "vendor and model_number and description are required fields for model":
#                 message = "incorrect error message thrown: {}".format(e.message)
#                 self.fail(message)
#             pass
#
#     def test_edit_model_non_unique_throws_exception(self):
#         user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
#                                    admin=True)
#         model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description")
#         try:
#             EditModel(user_id=user.id, password=user.password, model_id=model.id, vendor="vendor", model_number="model_number",
#                       description="description").execute()
#         except FieldCombinationNotUniqueException as e:
#             if e.message != "The combination of vendor and model_number must be unique for model":
#                 self.fail("incorrect error message thrown: {}".format(e.message))
#             pass
#
#     def test_edit_model_not_admin_throws_exception(self):
#         user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
#                                    admin=False)
#         try:
#             EditModel(user_id=user.id, password=user.password, model_id=1, vendor="vendor", model_number="model_number", description="description").execute()
#             self.fail("non admin permitted to use function")
#         except IllegalAccessException:
#             pass
#
#     def test_edit_unexisting_model_throws_exception(self):
#         user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
#                                    admin=True)
#         model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description")
#         try:
#             EditModel(user_id=user.id, password=user.password, model_id=model.id + 1, vendor="vendor", model_number="model_number", description="description").execute()
#             self.fail("No model of this id exists")
#         except EntryDoesNotExistException:
#             pass
#
#     def test_edit_model_succeeds(self):
#         user = User.objects.create(username="username", password="password", name="name", email="user@gmail.com",
#                                    admin=True)
#         model = EquipmentModel.objects.create(vendor="vendor", model_number="model_number", description="description")
#         EditModel(user_id=user.id, password=user.password, model_id=model.id, vendor="vendor", model_number="model_number", description="description").execute()
#         pass
#
#
