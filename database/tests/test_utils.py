from django.test import TestCase
from rest_framework.test import APIRequestFactory

from user_portal.models import PowerUser


class EndpointTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = PowerUser.objects.create_superuser('username', 'admin', 'email', 'DukeECE458', is_active=True)