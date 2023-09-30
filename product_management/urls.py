from django.urls import path
from .views import StaffHomeView,StaffReportUserGraphView

app_name =  'product_management'

urlpatterns = [
  path('staff_home/',StaffHomeView.as_view(), name='staff_home'),
  path('staff_reportusergraph/',StaffReportUserGraphView.as_view(), name='staff_reportusergraph'),

]