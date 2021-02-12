from enum import Enum

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from user_portal.models import PowerUser

TEST_ROOT = "http://127.0.0.1:8000/"

class EndpointTestCase(TestCase):
    class Endpoints(Enum):
        MODELS = TEST_ROOT + "models/"
        VENDORS = TEST_ROOT + "vendors?vendor={}"
        INSTRUMENT = TEST_ROOT + "models/"

        def fill(self, params):
            return self.value.format(*params)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = PowerUser.objects.create_superuser('username', 'admin', 'email', 'DukeECE458', is_active=True)
