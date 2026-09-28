from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'ok',
        'service': 'HR Performance Review System API',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/users/', include('apps.authentication.user_urls')),
    path('api/users/', include('apps.authentication.user_urls')),
    path('api/teams/', include('apps.organizations.urls')),
    path('api/evaluations/', include('apps.evaluations.urls')),
    path('api/reports/', include('apps.reports.urls')),
]
