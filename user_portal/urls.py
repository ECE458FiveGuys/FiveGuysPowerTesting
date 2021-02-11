from django.urls import include, re_path
from rest_framework import routers

from user_portal.views import ExtendedUserViewSet

router = routers.DefaultRouter()
router.register(r'users', ExtendedUserViewSet)

urlpatterns = (
    re_path(r"^auth/", include("djoser.urls.base")),
    re_path(r"^auth/", include(router.urls)),
    re_path(r"^auth/", include("djoser.urls.authtoken"))
)
