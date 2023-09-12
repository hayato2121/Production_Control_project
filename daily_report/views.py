from django.shortcuts import render

from django.views.generic.list import ListView
from django.views.generic.edit import (
    UpdateView, DeleteView, CreateView
)
from django.views.generic.base import TemplateView

from django.urls import reverse_lazy

from daily_report.models import Report
import os

from .forms import ReportStartForm

#ログイン状態
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
    
#作業start
class ReportStartView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('report', 'report_start.html')
    form_class = ReportStartForm
    success_url = reverse_lazy('daily_report:report_list')

    def form_valid(self, form):
        if form.is_valid(): #バリデーションする
            form.instance.user = self.request.user #ユーザー情報を設定
            form.save() #保存する。
        return super(ReportStartView, self).form_valid(form)
    
        

#作業終了
class ReportEndView(LoginRequiredMixin,TemplateView):
    template_name = os.path.join('report', 'report_end.html')



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

        #作業データ
        session_data = self.request.session.get('form_data',{})

        task_data = session_data.get('product','business')
        context['task_data'] = task_data

        #ユーザーデータ
        context['user'] = self.request.user
        return context
        
