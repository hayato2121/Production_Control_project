from django.shortcuts import render
from django.views import View

#from accounts.views import is_staff_user


from django.views.generic.base import TemplateView


import os
#staffユーザーしかアクセスできない

class StaffHomeView(TemplateView):
    template_name = os.path.join('staff', 'staff_home.html')