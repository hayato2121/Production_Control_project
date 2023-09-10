from django.urls import path
from .views import ReportListView

app_name =  'daily_report'

urlpatterns = [
    path('report_list/', ReportListView.as_view(), name='report_list'),
]