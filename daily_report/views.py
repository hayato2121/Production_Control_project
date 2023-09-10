from django.shortcuts import render

from django.views.generic.list import ListView

from daily_report.models import Report
import os

#ログイン状態
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

#作業一覧
class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = os.path.join('daily_report', 'report/report_list.html')

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)