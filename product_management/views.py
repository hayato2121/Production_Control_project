from typing import Any
from django.shortcuts import render, get_object_or_404
from django.views import View

from accounts.models import Users
from daily_report.models import Report, Products,Business
from accounts.models import Departments
from .models import Molding, Stock,Shipping

from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView
from django.views.generic.edit import (
    UpdateView, DeleteView, CreateView
)
from django.views.generic import DetailView
from django.views.generic.list import ListView
from datetime import datetime
from .forms import (
    StaffProductCreateForm, StaffBusinessCreateForm, 
    GraphYearMonthForm, StaffReportEditForm, StaffMoldingEditForm,
    StaffStockEditForm,StaffProductEditForm
)
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from django.views import View

import os

import matplotlib
matplotlib.use('Agg')
import japanize_matplotlib #グラフを文字化けしないようにする
import matplotlib.pyplot as plt
from django.db.models import Sum
import io
import base64
import numpy as np
import matplotlib.font_manager


#ログインしているユーザーを取得する。
@login_required
def employee_attendance(request):
    login_user = request.user
    attendance_info = login_user.attendance

    return render(request, 'staff_home.html', {'logged_in_user': login_user, 'attendance_info': attendance_info})

#上で取得したユーザー情報をリストとして表示する。
class StaffHomeView(LoginRequiredMixin,TemplateView):
    model = Users
    template_name = os.path.join('staff', 'staff_home.html')
    context_object_name = 'users'

   #部署ごとにログインユーザーを取得する
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #ユーザーがログインしているか確認
        if self.request.user.is_authenticated:
            # ログインしているユーザーの部署を取得
            login_user = self.request.user
            department_user = login_user.department.name

        # ログインユーザーの部署に基づいてユーザー情報を取得
            department_users = Users.objects.filter(department__name=department_user)

            context['department_users'] = department_users

        return context
 


#日報の集計グラフ------------------------------------------------------------------------
class StaffReportUserGraphView(LoginRequiredMixin,View):
    template_name = os.path.join('staff', 'staff_reportusergraph.html')

    def get(self, request, *args, **kwargs):

        #月と年を入力するフォーム
        form = GraphYearMonthForm(request.GET)
        # フォームが送信され、バリデーションが成功した場合
        if form.is_valid():
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            users = Users.objects.filter(department__name='製造部')
            products = Products.objects.all()

            user_data = {}  # ユーザーごとの優良数を入れる
        
            for user in users:
                user_data[user.username] = {product.name: 0 for product in products}
            #製品ごとの合計数
            for product in products:
                #優良数
                product_good_data = Report.objects.filter(
                    product=product, created_at__year=year, created_at__month=month,business__name='成形'
                    ).values('user__username').annotate(total_good_product=Sum('good_product'))
                for entry in product_good_data:
                    username = entry['user__username']
                    total_good_product = entry['total_good_product'] or 0
                    if username in user_data:
                        user_data[username][product.name] = total_good_product

            # グラフにデータを設定
            labels = [user.username for user in users]
            x = range(len(users))

            # グラフ描写
            plt.figure(figsize=(9, 4))

            plt.ylim(0, 100000) #y軸のラベルの範囲を指定0から1000000

            # ユーザごとにデータを積み上げて描写
            bottom_data = np.zeros(len(users), dtype=float)
            for product in products:
                product_good_data = [user_data[user.username][product.name] for user in users]
                plt.bar(x, product_good_data, label=product.name, bottom=bottom_data)
                bottom_data += product_good_data

            plt.xlabel('ユーザー',fontname = 'IPAexGothic')
            plt.ylabel('優良数',fontname = 'IPAexGothic')
            plt.xticks(x, labels, rotation=45)
            plt.tight_layout()
            plt.legend(prop = {"family" : "IPAexGothic"})

            # y軸の数に合わせた横線を追加
            for y_value in range(0, 100001, 20000):  # 適切な間隔を設定してください
                plt.axhline(y_value, color='gray', linestyle='--', linewidth=0.5)

            # グラフを画像ファイルとして保存
            image_stream = io.BytesIO()
            plt.savefig(image_stream, format='png')
            image_stream.seek(0)
            image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')
            plt.close()

            #テキスト状に集計結果を表示----------------------------------------------------------------------------------
            report_data = Report.objects.filter(product__in=products, created_at__year=year, created_at__month=month, business__name='成形')

            user_product_data = {}
            for user in users:
                user_product_data[user.username] = {
                    'products': {},
                    'total_good_product': 0,
                    'total_bad_product': 0
                }


            # クエリの結果を整理
            for entry in report_data:
                username = entry.user.username
                product_name = entry.product.name
                good_product = entry.good_product or 0
                bad_product = entry.bad_product or 0
                department = entry.user.department.name


                if username not in user_product_data:
                    user_product_data[username] = {
                        'products': {},
                        'total_good_product': 0,
                        'total_bad_product': 0,
                        'department': department  # ユーザーの部署情報を最初に追加
                    }

                if 'department' not in user_product_data[username]:
                    user_product_data[username]['department'] = department  # ユーザーの部署情報を最初に追加

                # ユーザーの部署が変更された場合に、新しい部署情報にアップデート
                if user_product_data[username]['department'] != department:
                    user_product_data[username]['products'] = {}  # プロダクト情報をリセット
                    user_product_data[username]['department'] = department


                if product_name not in user_product_data[username]['products']:
                    user_product_data[username]['products'][product_name] = {
                        'good_product': 0,
                        'bad_product': 0
                    }

                user_product_data[username]['products'][product_name]['good_product'] += good_product
                user_product_data[username]['products'][product_name]['bad_product'] += bad_product
                user_product_data[username]['total_good_product'] += good_product
                user_product_data[username]['total_bad_product'] += bad_product
            #---------------------------------------------------------------------------------------------------------


            context = {
                'chart_image': image_base64,  
                'form': form,
                'user_product_data': user_product_data,
            }

            return render(request, self.template_name, context)
    
        # フォームがバリデーションに失敗した場合
        context = {
            'chart_image': None, 
            'form': form,  
        }
        return render(request, self.template_name, context)
    


#製品ごとの成形数------------------------------------------------------------------------------------------------------
class StaffReportProductGraphView(LoginRequiredMixin,View):
    template_name = os.path.join('staff', 'staff_reportproductgraph.html')


    def get(self, request, *args, **kwargs):


        #月と年を入力するフォーム
        form = GraphYearMonthForm(request.GET)
        # フォームが送信され、バリデーションが成功した場合
        if form.is_valid():
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            products = Products.objects.all()

            product_data = {}  # ユーザーごとの優良数を入れる
        
            for product in products:
                product_data[product.name] = {
                    'total_good_product': 0,
                    'total_bad_product': 0,
                }

            #製品ごとの合計数
            for product in products:
                #優良数
                product_molding_data = Report.objects.filter(
                    product=product, created_at__year=year, created_at__month=month,business__name='成形'
                    ).values('user__username').annotate(total_good_product=Sum('good_product'),total_bad_product=Sum('bad_product'))
                total_good_product = product_molding_data.aggregate(total_good_product=Sum('good_product'))['total_good_product'] or 0
                total_bad_product = product_molding_data.aggregate(total_bad_product=Sum('bad_product'))['total_bad_product'] or 0
                product_data[product.name] = {
                    'total_good_product': total_good_product,
                    'total_bad_product': total_bad_product,
                }


            # グラフにデータを設定

            products_count = Products.objects.count()
            labels = [product.name for product in products]
            x = range(products_count)

            # グラフ描写
            plt.figure(figsize=(9, 4))
            plt.ylim(0, 100000) #y軸のラベルの範囲を指定0から1000000

            product_good_data = [product_data[product.name]['total_good_product'] for product in products]
            product_bad_data = [product_data[product.name]['total_bad_product'] for product in products]

            width = 0.35  # バーの幅を調整

            plt.bar(x, product_good_data, width, align='edge', label='優良数', alpha=0.7 ,)
            plt.bar(x, product_bad_data, width, align='center', label='不良数', alpha=0.7)
 
          
            plt.xlabel('製品名',fontname = 'IPAexGothic')
            plt.ylabel('優良数',fontname = 'IPAexGothic')
            plt.xticks(x, labels, rotation=45)
            plt.tight_layout()
            plt.legend(prop = {"family" : "IPAexGothic"})

            # y軸の数に合わせた横線を追加
            for y_value in range(0, 100001, 20000):  # 適切な間隔を設定してください
                plt.axhline(y_value, color='gray', linestyle='--', linewidth=0.5)

            # グラフを画像ファイルとして保存
            image_stream = io.BytesIO()
            plt.savefig(image_stream, format='png')
            image_stream.seek(0)
            image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')
            plt.close()

            #テキスト状に集計結果を表示----------------------------------------------------------------------------------
            report_data = Report.objects.filter(product__in=products, created_at__year=year, created_at__month=month, business__name='成形')

            products_data = {}
            for product in products:
                products_data[product.name] = {
                    'total_good_product': 0,
                    'total_bad_product': 0
                }

            # クエリの結果を整理
            for entry in report_data:
                product_name = entry.product.name
                good_product = entry.good_product or 0
                bad_product = entry.bad_product or 0

                products_data[product_name]['total_good_product'] += good_product
                products_data[product_name]['total_bad_product'] += bad_product

            #---------------------------------------------------------------------------------------------------------

            context = {
                'chart_image': image_base64,  
                'form': form,
                'products_data': products_data,
            }

            return render(request, self.template_name, context)
    
        # フォームがバリデーションに失敗した場合
        context = {
            'chart_image': None, 
            'form': form,  
        }
        return render(request, self.template_name, context)
    

#製品情報入力------------------------------------------------------------------------------------------------------
class StaffProductListView(LoginRequiredMixin,ListView):
    model = Products
    template_name = os.path.join('staff','staff_product_list.html')
    context_object_name = 'products'


class StaffProductEditView(LoginRequiredMixin,UpdateView):
    model = Products
    template_name = os.path.join('staff', 'staff_product_edit.html')
    form_class = StaffProductEditForm
    success_url = reverse_lazy('product_management:staff_product_list')

class StaffProductCreateView(LoginRequiredMixin,CreateView):
    template_name = os.path.join('staff', 'staff_product_create.html')
    form_class = StaffProductCreateForm
    success_url = reverse_lazy('product_management:staff_home')

    def form_valid(self, form):
        form.instance.create_at = datetime.now()
        form.instance.update_at = datetime.now()
        return super(StaffProductCreateView, self).form_valid(form)
    
class StaffProductDeleteView(LoginRequiredMixin,DeleteView):
    model = Products
    success_url = reverse_lazy('product_management:staff_product_list')
    template_name = os.path.join('staff', 'staff_product_delete.html')


#業務内容作成------------------------------------------------------------------------------------------------------
class StaffBusinessListView(LoginRequiredMixin,ListView):
    model = Business
    template_name = os.path.join('staff','staff_business_list.html')
    context_object_name = 'businesslist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['business_data'] = Business.objects.all() 
        context['department_data'] = Departments.objects.all()
        return context
    


class StaffBusinessCreateView(LoginRequiredMixin,CreateView):
    template_name = os.path.join('staff', 'staff_business_create.html')
    form_class = StaffBusinessCreateForm
    success_url = reverse_lazy('product_management:staff_business_list')

    def form_valid(self, form):
        form.instance.create_at = datetime.now()
        form.instance.update_at = datetime.now()
        return super(StaffBusinessCreateView, self).form_valid(form)
    
class StaffBusinessDeleteView(LoginRequiredMixin,DeleteView):
    model = Business
    success_url = reverse_lazy('product_management:staff_business_list')
    template_name = os.path.join('staff', 'staff_business_delete.html')

    

#日報表示------------------------------------------------------------------------------------------------------
class StaffReportListView(LoginRequiredMixin,View):
    template_name = os.path.join('staff', 'staff_report_list.html')


    def get(self, request, *args, **kwargs):

        #月と年を入力するフォーム
        form = GraphYearMonthForm(request.GET)
        # フォームが送信され、バリデーションが成功した場合

        report_list = []
        if form.is_valid():
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            report_data = Report.objects.filter(created_at__year=year, created_at__month=month)
            report_list = report_data

            context = {  
                'form': form,
                'report_list': report_list,
            }

            return render(request, self.template_name, context)
    
        # フォームがバリデーションに失敗した場合
        context = {
            'form': form,
            'report_list': report_list,
        }
        return render(request, self.template_name, context)

class StaffReportEditView(LoginRequiredMixin,UpdateView):
    model = Report
    template_name = os.path.join('staff', 'staff_report_edit.html')
    form_class = StaffReportEditForm
    success_url = reverse_lazy('daily_report:report_list')

    
class StaffReportDeleteView(LoginRequiredMixin,DeleteView):
    model = Report
    success_url = reverse_lazy('product_management:staff_report_list')
    template_name = os.path.join('staff', 'staff_report_delete.html')


#成形品表示------------------------------------------------------------------------------------------------------
class StaffMoldingListView(LoginRequiredMixin,ListView):
    model = Molding
    template_name = os.path.join('staff','staff_molding_list.html')
    context_object_name = 'staffmolding'

    #製品ごとの合計を計算して表示する
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        grouped_molding = Molding.objects.values('product__name').annotate(total_good_molding=Sum('good_molding'))

        context['grouped_molding'] = grouped_molding

        return context

class StaffMoldingEditView(LoginRequiredMixin,UpdateView):
    model = Molding
    template_name = os.path.join('staff','staff_molding_edit.html')
    form_class = StaffMoldingEditForm

    
class StaffMoldingDeleteView(LoginRequiredMixin,DeleteView):
    model = Molding
    success_url = reverse_lazy('product_management:staff_molding_list')
    template_name = os.path.join('staff', 'staff_molding_delete.html')



#ユーザー情報-----------------------------------------------------------------------------------
class StaffUserListView(LoginRequiredMixin,ListView):
    model = Users
    template_name = os.path.join('staff','staff_user_list.html')
    context_object_name = 'users'



class StaffUserDetailView(LoginRequiredMixin,DetailView):
    model = Users
    template_name = os.path.join('staff','staff_user_detail.html')
    context_object_name = 'user'


class StaffUserDeleteView(LoginRequiredMixin,DeleteView):
    model = Users
    success_url = reverse_lazy('product_management:staff_user_list')
    template_name = os.path.join('staff', 'staff_user_delete.html')


#在庫編集----------------------------------------------------------------------------------------------------------------------------------------------------------
class StaffStockListView(LoginRequiredMixin,ListView):
    model = Stock
    template_name = os.path.join('staff', 'staff_stock_list.html')
    context_object_name = 'staffstocks'

    #製品ごとの合計を計算して表示する
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        grouped_stocks = Stock.objects.values('product__name').annotate(total_stocks=Sum('stocks'))

        context['grouped_stocks'] = grouped_stocks
        return context


class StaffStockEditView(LoginRequiredMixin,UpdateView):
    model = Stock
    template_name = os.path.join('staff', 'staff_stock_edit.html')
    form_class = StaffStockEditForm
    success_url = reverse_lazy('product_management:staff_stock_list')

    

class StaffStockDeleteView(LoginRequiredMixin,DeleteView):
    model = Stock
    template_name = os.path.join('staff', 'staff_stock_delete.html')
    success_url = reverse_lazy('product_management:staff_stock_list')
    

#出荷リスト--------------------------------------------------------------------
class StaffShippingListView(LoginRequiredMixin,View):
    template_name = os.path.join('staff', 'staff_shipping_list.html')

    def get(self, request, *args, **kwargs):

        #月と年を入力するフォーム
        form = GraphYearMonthForm(request.GET)
        # フォームが送信され、バリデーションが成功した場合

        shipping_list = []
        if form.is_valid():
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            shipping_data = Shipping.objects.filter(shipping_day__year=year, shipping_day__month=month)
            shipping_list = shipping_data

            context = {  
                'form': form,
                'shipping_list': shipping_list,
            }

            return render(request, self.template_name, context)
    
        # フォームがバリデーションに失敗した場合
        context = {
            'form': form,
            'shipping_list': shipping_list,
        }
        return render(request, self.template_name, context)
    
       


class StaffShippingDetailView(LoginRequiredMixin,DetailView):
    model = Shipping
    template_name = os.path.join('staff','staff_shipping_detail.html')
    context_object_name = 'shippings'

    
class StaffShippingDeleteView(LoginRequiredMixin,DeleteView):
    model = Shipping
    success_url = reverse_lazy('product_management:staff_shipping_list')
    template_name = os.path.join('staff', 'staff_shipping_delete.html')
