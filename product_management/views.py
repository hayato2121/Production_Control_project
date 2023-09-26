from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
#from accounts.views import is_staff_user

from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic.base import TemplateView


import os

def is_staff_user(user):
    return user.groups.filter(name='staff').exists()

#staffユーザーしかアクセスできない
@method_decorator(user_passes_test(is_staff_user), name='dispatch')
class StaffHomeView(LoginRequiredMixin,TemplateView):
    template_name = os.path.join('staff', 'staff_home.html')