from django.urls import path
from .views import (
    StaffHomeView,StaffReportUserGraphView,StaffReportProductGraphView,
    StaffBusinessListView,StaffBusinessCreateView,StaffBusinessDeleteView,
    StaffProductCreateView,
    StaffReportListView, StaffReportEditView, StaffReportDeleteView,
    StaffMoldingListView, StaffMoldingEditView, StaffMoldingDeleteView,
    StaffUserListView,StaffUserDetailView,StaffUserDeleteView
)
app_name =  'product_management'

urlpatterns = [
  path('staff_home/',StaffHomeView.as_view(), name='staff_home'),
  path('staff_reportusergraph/',StaffReportUserGraphView.as_view(), name='staff_reportusergraph'),
  path('staff_reportproductgraph/',StaffReportProductGraphView.as_view(), name='staff_reportproductgraph'),

  path('staff_business_list/',StaffBusinessListView.as_view(), name='staff_business_list'),
  path('staff_business_create/',StaffBusinessCreateView.as_view(), name='staff_business_create'),
  path('staff_business_delete/<int:pk>/',StaffBusinessDeleteView.as_view(), name='staff_business_delete'),

  path('staff_product_create/', StaffProductCreateView.as_view(), name='staff_product_create'),

  path('staff_report_list/', StaffReportListView.as_view(), name='staff_report_list'),
  path('staff_report/<int:pk>/edit/', StaffReportEditView.as_view(), name='staff_report_edit'),
  path('staff_report_delete/<int:pk>/', StaffReportDeleteView.as_view(), name='staff_report_delete'),

  path('staff_molding_list/', StaffMoldingListView.as_view(), name='staff_molding_list'),
  path('staff_molding/<int:pk>/edit/', StaffMoldingEditView.as_view(), name='staff_molding_edit'),
  path('staff_molding_delete/<int:pk>/', StaffMoldingDeleteView.as_view(), name='staff_molding_delete'),

  path('staff_user_list/', StaffUserListView.as_view(), name='staff_user_list'),
  path('staff_user_detail/<int:pk>/', StaffUserDetailView.as_view(), name='staff_user_detail'),
  path('staff_user_delete/<int:pk>/', StaffUserDeleteView.as_view(), name='staff_user_delete'),

]