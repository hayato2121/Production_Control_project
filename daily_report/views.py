from django.shortcuts import render

from django.views.generic.list import ListView

from accounts.models import Users
import os

#ログイン状態
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

#作業一覧
class ReportListView(LoginRequiredMixin, ListView):
    model = Users
    template_name = os.path.join('daily_report', 'report/report_list.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_department_name'] = self.request.GET.get('user_department_name', None)
        return context