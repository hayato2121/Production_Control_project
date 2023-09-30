from django.urls import path
from .views import StaffHomeView,StaffReportUserGraphView,StaffReportProductGraphView
app_name =  'product_management'

urlpatterns = [
  path('staff_home/',StaffHomeView.as_view(), name='staff_home'),
  path('staff_reportusergraph/',StaffReportUserGraphView.as_view(), name='staff_reportusergraph'),
  path('staff_reportproductgraph/',StaffReportProductGraphView.as_view(), name='staff_reportproductgraph'),

]