from django.urls import path
from .views import (
    ReportListView ,ReportStartView ,ReportEndView,ReportDetailView,ReportDeleteView,
    RepoetStartInspectionView,ReportShippingEndView,ReportEndEditView
)
app_name =  'daily_report'

urlpatterns = [
    path('report_list/', ReportListView.as_view(), name='report_list'),
    path('report_start/',ReportStartView.as_view(), name='report_start'),
    path('report_detail/<int:pk>/',ReportDetailView.as_view(),name='report_detail'),
    path('report_detail/<int:pk>/end/', ReportEndView.as_view(), name='report_end'),
    path('report_detail/<int:pk>/endedit/', ReportEndEditView.as_view(), name='report_endedit'),
    path('report_delete/<int:pk>/',ReportDeleteView.as_view(), name='report_delete'),
    path('report_start_inspection/',RepoetStartInspectionView.as_view(),name='report_start_inspection'),
    path('report_detail/<int:pk>/shippingend/', ReportShippingEndView.as_view(), name='report_shippingend'),
]
