from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import SmetaCreateAPIView, smeta_details, rate_smeta, download_log, delete_log, view_log, export_filtered_log


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
    path('smeta/<uuid:uuid>/', smeta_details, name='smeta-details'),
    path('api/rate-smeta/<uuid:uuid>/', rate_smeta, name='rate-smeta'),
    path('api/swagger/', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
    path('logs/view/<str:file_name>/', view_log, name='view_log'),
    path('logs/download/<str:file_name>/', download_log, name='download_log'),
    path('logs/delete/<int:pk>/', delete_log, name='delete_log'),
    path('logs/export/<int:filter_id>/', export_filtered_log, name='export_filtered_log'),
]
