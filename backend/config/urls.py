from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.evaluations.views import my_review
from apps.reports.views import admin_status, dashboard_stats, team_analytics

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
    path('api/teams/', include('apps.organizations.urls')),
    path('api/evaluations/', include('apps.evaluations.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/employee/evaluation/', my_review, name='employee-evaluation-alias'),
    path('api/admin/team-analytics/', team_analytics, name='admin-team-analytics'),
    path('api/admin/status/', admin_status, name='admin-status'),
    path('api/admin/dashboard-stats/', dashboard_stats, name='admin-dashboard-stats'),
    
    # SPA catch-all fallback (all non-API and non-admin routes render Vue 3 index.html)
    re_path(r'^(?!api/|admin/|static/).*$', TemplateView.as_view(template_name='index.html'), name='spa-fallback'),
]
