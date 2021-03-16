import base64

import requests
from djoser import serializers
from djoser.conf import settings
from djoser.serializers import TokenSerializer
from djoser.views import UserViewSet
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from database.enums import UserEnum
from user_portal.models import User
from user_portal.secrets import OAuthEnum
from user_portal.serializers import CustomUserSerializer, IsStaffSerializer


class ExtendedUserViewSet(UserViewSet):
    queryset = User.objects.all()
    filterset_fields = [UserEnum.USERNAME.value]
    search_fields = [UserEnum.USERNAME.value]
    ordering_fields = [UserEnum.USERNAME.value]

    def get_queryset(self):
        user = self.request.user
        queryset = super(UserViewSet, self).get_queryset()
        if (
                settings.HIDE_USERS
                and self.action == "list"
                and not (user.is_staff or user.has_perm('user_portal.add_user'))
        ):
            queryset = queryset.filter(pk=user.pk)
        return queryset

    def get_serializer_class(self):
        if self.action == 'update_admin_status':
            return IsStaffSerializer
        return super(ExtendedUserViewSet, self).get_serializer_class()

    @action(['post'], detail=True)
    def deactivate(self, request, pk, *args, **kwargs):
        user = User.objects.get(pk=pk)
        user.is_active = False
        user.save()
        user_serializer = serializers.UserSerializer(user)
        return Response(user_serializer.data)

    @action(['post'], detail=True)
    def activate(self, request, pk, *args, **kwargs):
        user = User.objects.get(pk=pk)
        user.is_active = True
        user.save()
        user_serializer = serializers.UserSerializer(user)
        return Response(user_serializer.data)

    @action(['post'], detail=True)
    def update_admin_status(self, request, pk, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(pk=pk)
        user.is_staff = serializer.data['is_staff']
        user.save()

        user_serializer = serializers.UserSerializer(user)
        return Response(user_serializer.data)

    @action(['get'], detail=False, url_path='list/oauth')
    def oauth(self, request, *args, **kwargs):
        return Response(CustomUserSerializer(User.objects.oauth_users(), many=True).data)


class OAuthView(APIView):
    """
    View to login using OAuth
    """
    permission_classes = [permissions.AllowAny]

    @staticmethod
    def format_auth_string():
        string = f"{OAuthEnum.CLIENT_ID.value}:{OAuthEnum.CLIENT_SECRET.value}"
        data = base64.b64encode(string.encode())
        return data.decode("utf-8")

    def post(self, request, *args, **kwargs):
        oauth_code = request.data.get('oauth_code')

        auth = self.format_auth_string()

        url = "https://oauth.oit.duke.edu/oidc/token"

        env = request.data.get('env')
        if env == 'local':
            redirect_uri = "http://localhost:3000/oauth/consume"
        elif env == 'dev':
            redirect_uri = OAuthEnum.DEV_REDIRECT_URI.value
        else:
            redirect_uri = OAuthEnum.PROD_REDIRECT_URI.value

        payload_for_token = {
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": oauth_code
        }
        headers_for_token = {
            "content-type": "application/x-www-form-urlencoded",
            "authorization": f"Basic {auth}"
        }

        response = requests.post(url, data=payload_for_token, headers=headers_for_token)

        try:
            oauth_token = response.json()['access_token']
        except KeyError:
            return Response({'redirect_uri_used': redirect_uri,
                             'code_given': oauth_code}, status=401)

        headers_for_user = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {oauth_token}"
        }

        response = requests.get('https://oauth.oit.duke.edu/oidc/userinfo', headers=headers_for_user)

        user_info = response.json()

        name = user_info['name']
        username = email = user_info['sub']

        user = User.objects.filter(username=username)

        if not user.exists():
            User.objects.create_oauth_user(username=username, name=name, email=email)

        token, created = Token.objects.get_or_create(user=User.objects.get(username=username))
        token_serializer = TokenSerializer(token)

        return Response(token_serializer.data)
