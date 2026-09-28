from django.urls import path

from apps.reports.views import (
    admin_status,
    dashboard_kpi,
    dashboard_stats,
    export_csv,
    score_table,
    team_analytics,
)

urlpatterns = [
    path('dashboard-kpi/', dashboard_kpi, name='dashboard-kpi'),
    path('dashboard-stats/', dashboard_stats, name='dashboard-stats'),
    path('score-table/', score_table, name='score-table'),
    path('export-csv/', export_csv, name='export-csv'),
    path('team-analytics/', team_analytics, name='team-analytics'),
    path('status/', admin_status, name='reports-admin-status'),
]
