from django.urls import path
from .views import StaffHomeView

app_name =  'product_management'

urlpatterns = [
  path('staff_home/',StaffHomeView.as_view(), name='staff_home'),
]