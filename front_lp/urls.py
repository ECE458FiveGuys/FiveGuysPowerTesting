from django.urls import path, include
from front_lp import views as v_lp
from django.views.decorators.csrf import csrf_exempt

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    #path(r'^$', csrf_exempt(v_lp.home)),
    #path(r'^$', csrf_exempt(v_lp.createmodel)),
    path('login/', v_lp.loginpage),
    path('deleteconfirmation/', v_lp.deleteconfirmation),
    path('createmodel/', v_lp.createmodel),
    path('createinstrument/', v_lp.createinstrument),
    path('createuser/', v_lp.createuser),
    path('tempMainPage/', v_lp.tempMainPage),
    path('home/', v_lp.home)
]
