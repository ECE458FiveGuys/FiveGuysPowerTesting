from django.urls import path, include
from front_lp import views as v_lp

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('login/', v_lp.loginpage),
    path('deleteconfirmation/', v_lp.deleteconfirmation),
    path('createmodel/', v_lp.createmodel),
    path('createinstrument/', v_lp.createinstrument),
    path('createuser/', v_lp.createuser),
    path('tempMainPage/', v_lp.tempMainPage),
    path('home/', v_lp.home)
]
