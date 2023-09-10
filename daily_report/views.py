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
    template_name = os.path.join('report', 'report_list.html')

    #ログインユーザーしか自分のデータを見ることができない設定
    def get_queryset(self):
        user_obj = self.request.user
        if user_obj.is_authenticated:
             qs = Report.objects.filter(user=user_obj)
        else:
            qs = Report.objects.none()
        return qs
    
    #ユーザーデータをテンプレートに渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context