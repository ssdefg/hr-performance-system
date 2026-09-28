from django.urls import path

from apps.reports.views import dashboard_kpi, export_csv, score_table

urlpatterns = [
    path('dashboard-kpi/', dashboard_kpi, name='dashboard-kpi'),
    path('score-table/', score_table, name='score-table'),
    path('export-csv/', export_csv, name='export-csv'),
]
