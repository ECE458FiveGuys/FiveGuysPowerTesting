from django.urls import path
from detail_views import views as dv


urlpatterns = [
    path('model-details/<str:pk>', dv.model_detail_page, name='model-details'),
    path('instrument-details/<str:serial>', dv.instrument_detail_page, name='instrument-details'),
    path('pdf/<str:serial>', dv.pdf_gen),

]
