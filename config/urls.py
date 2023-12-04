from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import permissions
from ritual import admin_views

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for my app",
        # ... другие настройки ...
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    path("", include("django_nextjs.urls")),
    path('admin/send-message/<int:user_id>/', admin_views.send_admin_message, name='send_admin_message'),

    path('admin/', admin.site.urls),
    path('api/', include('ritual.urls')),
    path('api/order/', include('order.urls')),
    path('api/pay/', include('pay.urls')),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
