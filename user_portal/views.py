import requests

from rest_framework.views import APIView

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
    authentication_classes = []

    @action(['post'], detail=False)
    def login(self, request, *args, **kwargs):
        oauth_token = request.data.get('oauth_token')
        headers = {
            'Authorization': "Bearer {}".format(oauth_token)
        }
        response = requests.post('https://oauth.oit.duke.edu/oidc/userinfo', headers=headers)

        if "OAUTH_TOKEN_URL" in os.environ:
            url = os.environ["OAUTH_TOKEN_URL"]
        else:
            url = "https://oauth.oit.duke.edu/oidc/token"

        payload = urllib.parse.urlencode({
            'grant_type': "authorization_code",
            'redirect_uri': os.environ["OAUTH_REDIRECT_URI"],
            'code': code
        })
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'authorization': "Basic {}".format(auth)
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        print("Here is your auth token: ")
        print(json.loads(response.text))
        return json.loads(response.text)
