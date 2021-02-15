"""FiveGuysPowerTesting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from page_views import views as v
from django.urls import path, include
from front_lp import views as v_lp

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include('detail_views.urls')),
    path('', include('database.urls')),
    path('model/', v.modelpage),
    path('instrument/', v.instrumentpage),
    path('', include('user_portal.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include('front_lp.urls'))
]
