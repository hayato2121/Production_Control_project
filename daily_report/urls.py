from django.urls import path
from .views import ReportListView,ReportStartView

app_name =  'daily_report'

urlpatterns = [
    path('report_list/', ReportListView.as_view(), name='report_list'),
    path('report_start/',ReportStartView.as_view(), name='report_start')
]