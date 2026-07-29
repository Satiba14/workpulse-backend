from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.workforce.api.v1.views.document import EmployeeDocumentUploadView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.workforce.api.v1.urls')),

    # API Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/employees/<uuid:pk>/documents/',
         EmployeeDocumentUploadView.as_view(),
         name='employee-document-upload'),
    path('api/v1/employees/<uuid:pk>/documents/<uuid:doc_id>/',
     EmployeeDocumentUploadView.as_view(), name='employee-document-delete'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
