from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from database.models import Model
from database.services.model_services.select_models import SelectModels


class SelectModelsTestCase(TestCase):

    def test_select_models(self):
        Model.objects.create(vendor="vendor", model_number="model_number", description="description")
        try:
            SelectModels().execute().get(vendor="vendor")
            pass
        except ObjectDoesNotExist:
            self.fail("Added model could not be found")

