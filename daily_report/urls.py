from django.urls import path
from .views import (
    ReportListView ,ReportStartView ,ReportEndView,ReportDetailView
)
app_name =  'daily_report'

urlpatterns = [
    path('report_list/', ReportListView.as_view(), name='report_list'),
    path('report_start/',ReportStartView.as_view(), name='report_start'),
    path('report_detail/<int:pk>/',ReportDetailView.as_view(),name='report_detail'),
    path('report_detail/<int:pk>/end/', ReportEndView.as_view(), name='report_end'),
]
