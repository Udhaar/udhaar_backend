from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.urls.conf import include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import os

schema_view = get_schema_view(
    openapi.Info(
        title="Udhaar API",
        default_version='v1',
        description="",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=os.environ.get("BASE_URL")
)

urlpatterns = [
    url(r'^swagger/$', schema_view.with_ui('swagger',
        cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc',
        cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('api/user/', include('user.urls')),
    path('api/transaction/', include('transaction.urls')),
    path('api/balance/', include('balance.urls')),
    path('api/notification/', include('notification.urls')),
]
