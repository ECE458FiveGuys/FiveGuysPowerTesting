# import base64
#
# import requests
# from django.test import TestCase
# from djoser.serializers import TokenSerializer
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token
#
# # Create your tests here.
# from user_portal.models import PowerUser
# from user_portal.secrets import OAuthEnum
#
#
# class UserTestCase(TestCase):
#     TEST_ROOT = "http://127.0.0.1:8000/auth/"
#
#     def format_auth_string(self):
#         string = "{}:{}".format(OAuthEnum.CLIENT_ID.value, OAuthEnum.CLIENT_SECRET.value)
#         data = base64.b64encode(string.encode())
#         return data.decode("utf-8")
#
#     def test_token(self):
#         oauth_code = 'njfKMz'
#
#         auth = self.format_auth_string()
#         url = "https://oauth.oit.duke.edu/oidc/token"
#
#         payload_for_token = {
#             'grant_type': "authorization_code",
#             'redirect_uri': 'http://localhost:3000/oauth/consume',
#             'code': oauth_code
#         }
#         headers_for_token = {
#             'content-type': "application/x-www-form-urlencoded",
#             'authorization': "Basic {}".format(auth)
#         }
#
#         response = requests.post(url, data=payload_for_token, headers=headers_for_token)
#         oauth_token = response.json()['access_token']
#
#         headers_for_user = {
#             'content-type': "application/x-www-form-urlencoded",
#             'Authorization': "Bearer {}".format(oauth_token)
#         }
#
#         response = requests.get('https://oauth.oit.duke.edu/oidc/userinfo', headers=headers_for_user)
#         print(response.json())
#
#         user_info = response.json()
#
#         name = user_info['name']
#         username = email = user_info['sub']
#
#         user = PowerUser.objects.filter(username=username)
#
#         if not user.exists():
#             PowerUser.objects.create_oauth_user(username=username, name=name, email=email)
#
#         token, created = Token.objects.get_or_create(user=PowerUser.objects.get(username=username))
#         token_serializer = TokenSerializer(token)
#
#         print(token_serializer.data)
#
#         return Response(token_serializer.data)
