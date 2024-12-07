from django.urls import re_path
from rest_framework.routers import DefaultRouter

#from assignments.views import AssignmentViewSet

#from rest_framework_swagger.views import get_swagger_view
from django.urls import path
from .views import  *
from . import views
from rest_framework.schemas import get_schema_view

from django.views.generic import TemplateView




schema_view = get_swagger_view(title='Offer API')

urlpatterns = [    
        path("api/doc", schema_view),
            path('api/restdoc', get_schema_view(
                title="Offer API",
                description="Offer API …",
                version="1.0.0"
                ), name='openapi-schema'),
            path('api/doc', TemplateView.as_view(
                template_name='swagger-ui.html',
                extra_context={'schema_url':'openapi-schema'}
            ), name='swagger-ui'),    
            path('api/wh', WhView.as_view()),
            path('api/get_offer_data/<str:hash>', views.get_offer_data),
            path('api/in_data', InDataView.as_view()),       
            path('order/<str:order_number>/', order_detail, name='order_detail'),
    ]
    
router = DefaultRouter()
router.register(r"api/offer", OfferViewSet, basename="offer")
router.register(r"api/file_upload_image", FileUploadImageViewSet, basename="file_upload_image")

urlpatterns += router.urls

assignments_urlpatterns = urlpatterns