from django.urls import path, include
from create_pages import views as v_lp
from django.views.decorators.csrf import csrf_exempt

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('createmodel/', v_lp.createmodel),
    path('createinstrument/', v_lp.createinstrument),
    path('createuser/', v_lp.createuser),
    path('login/', v_lp.login),
    path('intermediatepage/', v_lp.intermediatepage)
]
