import base64

import requests
from djoser.serializers import TokenSerializer
from rest_framework.authtoken.models import Token

from rest_framework.views import APIView

from user_portal.secrets import OAuthEnum
from user_portal.serializers import IsStaffSerializer
from djoser import serializers
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from user_portal.models import PowerUser
from database.model_enums import UserEnum


class ExtendedUserViewSet(viewsets.ModelViewSet):
    queryset = PowerUser.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = [UserEnum.USERNAME.value]
    search_fields = [UserEnum.USERNAME.value]
    ordering_fields = [UserEnum.USERNAME.value]

    def get_serializer_class(self):
        if self.action == 'update_admin_status':
            return IsStaffSerializer
        return serializers.UserSerializer

    @action(['post'], detail=True)
    def deactivate(self, request, pk, *args, **kwargs):
        user = PowerUser.objects.get(pk=pk)
        user.is_active = False
        user.save()
        user_serializer = serializers.UserSerializer(user)
        return Response(user_serializer.data)

    @action(['post'], detail=True)
    def update_admin_status(self, request, pk, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = PowerUser.objects.get(pk=pk)
        user.is_staff = serializer.data['is_staff']
        user.save()

        user_serializer = serializers.UserSerializer(user)
        return Response(user_serializer.data)


class OAuthView(APIView):
    """
    View to login using OAuth
    """
    permission_classes = [permissions.AllowAny]

    def format_auth_string(self):
        string = "{}:{}".format(OAuthEnum.CLIENT_ID.value, OAuthEnum.CLIENT_SECRET.value)
        data = base64.b64encode(string.encode())
        return data.decode("utf-8")

    def post(self, request, *args, **kwargs):
        oauth_code = request.data.get('oauth_code')

        auth = self.format_auth_string()

        url = "https://oauth.oit.duke.edu/oidc/token"

        env = request.data.get('env')
        if env == 'local':
            redirect_uri = 'http://localhost:3000/oauth/consume'
        elif env == 'dev':
            redirect_uri = OAuthEnum.REDIRECT_URI.value
        else:
            redirect_uri = 'http://localhost:3000/oauth/consume'

        payload_for_token = {
            'grant_type': "authorization_code",
            'redirect_uri': redirect_uri,
            'code': oauth_code
        }
        headers_for_token = {
            'content-type': "application/x-www-form-urlencoded",
            'authorization': "Basic {}".format(auth)
        }

        response = requests.post(url, data=payload_for_token, headers=headers_for_token)

        try:
            oauth_token = response.json()['access_token']
        except KeyError:
            return Response({'redirect_uri_used': redirect_uri,
                             'code_given': oauth_code}, status=401)

        headers_for_user = {
            'content-type': "application/x-www-form-urlencoded",
            'Authorization': "Bearer {}".format(oauth_token)
        }

        response = requests.get('https://oauth.oit.duke.edu/oidc/userinfo', headers=headers_for_user)

        user_info = response.json()

        name = user_info['name']
        username = email = user_info['sub']

        user = PowerUser.objects.filter(username=username)

        if not user.exists():
            PowerUser.objects.create_oauth_user(username=username, name=name, email=email)

        token, created = Token.objects.get_or_create(user=PowerUser.objects.get(username=username))
        token_serializer = TokenSerializer(token)

        return Response(token_serializer.data)
