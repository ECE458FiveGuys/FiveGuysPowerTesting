from django.urls import include, re_path
from rest_framework import routers

from user_portal.views import ExtendedUserViewSet, OAuthView

router = routers.DefaultRouter()
router.register(r'users', ExtendedUserViewSet)

urlpatterns = (
    re_path('', include("djoser.urls.base")),
    re_path('', include(router.urls)),
    re_path('', include("djoser.urls.authtoken")),
    re_path('oauth/login/', OAuthView.as_view())
)
