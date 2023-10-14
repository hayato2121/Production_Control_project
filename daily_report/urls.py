from django.urls import path
from .views import (
    ReportListView ,ReportStartView ,ReportEndView,ReportDetailView,ReportDeleteView,
    RepoetStartInspectionView,ReportEndEditView,ReportLogoutConfirm,
    StockEditView,StockListView,StockDeleteView,
    ShippingStartView,ShippingDetailView,ShippingListView,ShippingDeleteView
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

    path('shipping_list/', ShippingListView.as_view(), name='shipping_list'),
    path('shipping_start/', ShippingStartView.as_view(), name='shipping_start'),
    path('shipping_detail/<int:pk>/',ShippingDetailView.as_view(),name='shipping_detail'),
    path('shipping_delete/<int:pk>/',ShippingDeleteView.as_view(),name='shipping_delate'),

    path('stocks_list/', StockListView.as_view(), name='stock_list'),
    path('stocks/<int:pk>/edit/', StockEditView.as_view(), name='stock_edit'),
    path('stocks_delete/<int:pk>/', StockDeleteView.as_view(), name='stock_delete'),

    path('logout/',ReportLogoutConfirm.as_view(),name='logout'),
]
