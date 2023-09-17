from typing import Any
from django.shortcuts import render,redirect

from django.views.generic.list import ListView
from django.views.generic.edit import (
    UpdateView, DeleteView, CreateView
)
from django.views.generic import DetailView
from django.views.generic.base import TemplateView

from django.urls import reverse_lazy

from daily_report.models import Report
import os

from .forms import ReportStartForm, ReportEndForm

#ログイン状態
from django.contrib.auth.mixins import LoginRequiredMixin

from datetime import date

from django.http import JsonResponse
# Create your views here.
    
#作業start
class ReportStartView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('report', 'report_start.html')
    form_class = ReportStartForm
    success_url = reverse_lazy('daily_report:report_list')

    def form_valid(self, form):
        # ログインしているユーザー情報をフォームにセット
        form.instance.user = self.request.user
        return super(ReportStartView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # フォームにユーザー情報を渡す
        return kwargs

        
#作業詳細
class ReportDetailView(LoginRequiredMixin,DetailView):
    model = Report
    template_name = os.path.join('report', 'report_detail.html')
    context_object_name = 'reportdetail'

    def get_queryset(self):
        return Report.objects.all()

#作業終了
class ReportEndView(LoginRequiredMixin,UpdateView):
    model = Report
    form_class = ReportEndForm
    template_name = os.path.join('report', 'report_end.html')
    success_url = reverse_lazy('daily_report:report_list')

    def form_valid(self, form):
        if form.is_valid():
            #good_productの計算
            good_product = self.object.product.quantity * form.cleaned_data['sets'] - form.cleaned_data['bad_product']
            self.object.good_product = good_product 
            self.object.save()  
            return super().form_valid(form)
        else:
            errors = form.errors
            for field, messages in errors.items():
                for message in messages:
                    # エラーメッセージをログに記録する例
                    print(f"Validation error for field '{field}': {message}")

        return self.render_to_response(self.get_context_data(form=form))
    
    #フォームに初期値を渡す
    def get_initial(self):
        initial = super().get_initial()

        return initial
    
    #フォームにユーザー情報をわたし、部署ごとの業務内容を選択できるようにする。
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs

    

#作業一覧
class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = os.path.join('report', 'report_list.html')
    context_object_name = 'reports'


    #ログインユーザーしか自分のデータを見ることができない設定
    def get_queryset(self):
        today = date.today()
        user_obj = self.request.user
        if user_obj.is_authenticated:
             qs = Report.objects.filter(user=user_obj,created_at__date = today)
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
    

class ReportDeleteView(LoginRequiredMixin,DeleteView):
    model = Report
    success_url = reverse_lazy('daily_report:report_list')
    template_name = os.path.join('report', 'report_delete.html')
   

    


 
    

