from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import SmetaCreateAPIView, smeta_details, rate_smeta


schema_view = get_schema_view(
   openapi.Info(
      title="Smeta API",
      default_version='v1',
      description="Swagger API Документация",
   ),
   permission_classes=(permissions.IsAdminUser,),
)

urlpatterns = [
    path('api/smeta_create/', SmetaCreateAPIView.as_view(), name='smeta-create'),
    path('smeta/<str:uuid>/', smeta_details, name='smeta-details'),
    path('rate-smeta/<str:uuid>/', rate_smeta, name='rate-smeta'),
    path('api/swagger/', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
]
