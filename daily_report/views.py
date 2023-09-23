from typing import Any
from django.shortcuts import render,redirect, get_object_or_404

from django.views.generic.list import ListView
from django.views.generic.edit import (
    UpdateView, DeleteView, CreateView
)
from django.views.generic import DetailView
from django.views.generic.base import TemplateView

from django.urls import reverse_lazy

from daily_report.models import Report
from product_management.models import Molding, Stock
import os

from .forms import ReportStartForm, ReportEndForm, ReportStartInspectionForm

#ログイン状態
from django.contrib.auth.mixins import LoginRequiredMixin

from datetime import date

from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your views here.
    
#作業start----------------------------------------------------------------------------------------------------------------------------------------------------------
class ReportStartView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('report', 'report_start.html')
    form_class = ReportStartForm
    success_url = reverse_lazy('daily_report:report_list')

    def form_valid(self, form):
        # ログインしているユーザー情報をフォームにセット
        form.instance.user = self.request.user
        form.instance.status = '実行中'
        return super(ReportStartView, self).form_valid(form)
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # フォームにユーザー情報を渡す
        return kwargs  


        
#作業詳細----------------------------------------------------------------------------------------------------------------------------------------------------------
class ReportDetailView(LoginRequiredMixin,DetailView):
    model = Report
    template_name = os.path.join('report', 'report_detail.html')
    context_object_name = 'reportdetail'

    def get_queryset(self):
        return Report.objects.all()
    
    #moldingのデータから優良数と不良数を持ってくる.確認のために表示するためなので、formは入れない
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.department.name == '検査部':
            report_lot_number = self.object.lot_number
            molding = Molding.objects.filter(lot_number = report_lot_number).first()

            context['inspection_good_molding'] = molding.good_molding
            context['inspection_bad_molding'] = molding.bad_molding
            context['inspection_molding_user'] = molding.user.username

        return context
            

#作業終了----------------------------------------------------------------------------------------------------------------------------------------------------------
class ReportEndView(LoginRequiredMixin,UpdateView):
    model = Report
    form_class = ReportEndForm
    template_name = os.path.join('report', 'report_end.html')
    success_url = reverse_lazy('daily_report:report_list')


    def form_valid(self, form):
        if form.is_valid():

            #現在のlot_numberを取得して、同じlot_numberからmoldingデータを取りだす。
            lot_number = self.object.lot_number
            molding_queryset = Molding.objects.filter(lot_number=lot_number)
            if molding_queryset.exists():
                first_molding = molding_queryset.first()

                good_molding = first_molding.good_molding
                molding_user = first_molding.user 
                molding_created_at = first_molding.created_at 
            else:
                good_molding = None
                molding_user = None
                molding_created_at = None
                        
            
            #good_productの計算
            if self.object.business.name == '成形' :
                good_product = self.object.product.quantity * form.cleaned_data['sets'] - form.cleaned_data['bad_product']
                self.object.good_product = good_product   
            elif self.object.business.name == '検査':
                good_product = good_molding - form.cleaned_data['bad_product']
                self.object.good_product = good_product
            else:
                self.object.good_product = None
            self.object.save()

            #status変更
            form.instance.status = '終了'

            response = super().form_valid(form)

            #業務内容が成形の時のみ成形モデルに送る
            if self.object.business.name == '成形':
                #編集したReportデータを取得しMoldingモデルに同時にCreateする
                molding_data = {
                    'product' : self.object.product,
                    'user': self.object.user,
                    'lot_number': self.object.lot_number,
                    'good_molding': self.object.good_product,
                    'bad_molding': self.object.bad_product,
                    'memo' : self.object.memo,
                }

                #同じlot_numberがある場合は、データを更新する
                molding, created = Molding.objects.get_or_create(lot_number=self.object.lot_number,defaults=molding_data)
                if not created:
                    #lot_numberがかぶっていれば更新
                    for key, value in molding_data.items():
                        setattr(molding, key, value)
                    molding.save()

            if self.object.business.name == '検査':
                stock_date = {
                    'product': self.object.product,
                    'lot_number': self.object.lot_number,
                    'stocks': self.object.good_product,
                    'molding_user':molding_user,
                    'molding_time':molding_created_at,
                    'inspection_user': self.object.user,
                    'memo': self.object.memo,
                }
            
                stock, created = Stock.objects.get_or_create(lot_number=self.object.lot_number,defaults=stock_date)
                if not created:
                    #lot_numberがかぶっていれば更新
                    for key, value in stock_date.items():
                        setattr(stock, key, value)
                    stock.save()

            return response
            
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
    
    

#作業一覧----------------------------------------------------------------------------------------------------------------------------------------------------------
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
    


#作業削除----------------------------------------------------------------------------------------------------------------------------------------------------------
class ReportDeleteView(LoginRequiredMixin,DeleteView):
    model = Report
    success_url = reverse_lazy('daily_report:report_list')
    template_name = os.path.join('report', 'report_delete.html')


   

#作業start(検査業務)----------------------------------------------------------------------------------------------------------------------------------------------------------
class RepoetStartInspectionView(LoginRequiredMixin,CreateView):
    template_name = os.path.join('report', 'report_start_inspection.html')
    form_class = ReportStartInspectionForm
    success_url = reverse_lazy('daily_report:report_list')

    def form_valid(self, form):
        # ログインしているユーザー情報をフォームにセット
        form.instance.user = self.request.user
        form.instance.status = '実行中'

        molding_lot_number = form.cleaned_data['molding_lot_number']
        molding = Molding.objects.filter(lot_number=molding_lot_number).first()

        if molding:
            report = form.save(commit=False)
            report.product = molding.product
            report.lot_number = molding.lot_number
            
            if form.cleaned_data['business']:
                report.business = form.cleaned_data['business']
            report.save()
            
        return super(RepoetStartInspectionView, self).form_valid(form)
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # フォームにユーザー情報を渡す
        return kwargs  


 
    

