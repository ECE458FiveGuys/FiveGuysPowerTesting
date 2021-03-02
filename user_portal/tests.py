import base64

import requests
from django.test import TestCase

# Create your tests here.

class UserTestCase(TestCase):
    TEST_ROOT = "http://127.0.0.1:8000/auth/"

    def format_auth_string(self):
        string = "{}:{}".format("ece458_2021_s_dpk14", "")
        data = base64.b64encode(string.encode())
        return data.decode("utf-8")


    def test_token(self):
        oauth_token = 'Or0idj'
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'Authorization': "Basic {}".format(oauth_token)
        }

        response = requests.post('https://oauth.oit.duke.edu/oidc/userinfo', headers=headers)
        print(response.json())
