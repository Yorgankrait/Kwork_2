from django.urls import path
from .views import SmetaCreateAPIView


urlpatterns = [
    path('smeta_create/', SmetaCreateAPIView.as_view(), name='smeta')
]
