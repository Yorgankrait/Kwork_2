from django.urls import path

from .views import SmetaCreateAPIView, smeta_details, rate_smeta


urlpatterns = [
    path('smeta_create/', SmetaCreateAPIView.as_view(), name='smeta'),
    path('smeta/<str:number>/', smeta_details, name='smeta_details'),
    path('rate-smeta/<str:number>/', rate_smeta, name='rate_smeta'),
]
