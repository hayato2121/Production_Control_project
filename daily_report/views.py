
from django.shortcuts import render,redirect, get_object_or_404

from django.views.generic.list import ListView
from django.views.generic.edit import (
    UpdateView, DeleteView, CreateView
)
from django.views.generic import DetailView

from django.urls import reverse_lazy

from django.db.models import Sum
from daily_report.models import Report, Business
from product_management.models import Molding, Stock, Shipping
import os

from .forms import (ReportStartForm, ReportEndForm, ReportStartInspectionForm,
                    ReportEndEditForm,StockEditForm,ShippingStartForm
                    
)

from daily_report.models import Products

from django.http import JsonResponse
#ログイン状態
from django.contrib.auth.mixins import LoginRequiredMixin

from datetime import date

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

            if molding:
                context['inspection_good_molding'] = molding.good_molding
                context['inspection_bad_molding'] = molding.bad_molding
                context['inspection_molding_user'] = molding.user.username
            else:
                context['inspection_good_molding'] = None
                context['inspection_bad_molding'] = None
                context['inspection_molding_user'] = None
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
    
#作業終了後編集-------------------------------------------------------------------------------------------------------------

class ReportEndEditView(LoginRequiredMixin,UpdateView):
    model = Report
    form_class = ReportEndEditForm
    template_name = os.path.join('report', 'report_end_edit.html')
    success_url = reverse_lazy('daily_report:report_list')

      #フォームにユーザー情報をわたし、部署ごとの業務内容を選択できるようにする。
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs
    
    #endeditで編集した内容を同じlot_numberのmodelとstockにも反映させる
    def form_valid(self, form):
        if form.is_valid():
            if self.object.business.name == '成形':
                #Molding モデルを更新するための情報を収集
                good_product = form.cleaned_data['good_product']
                bad_product = form.cleaned_data['bad_product']
                user = form.cleaned_data['user']
                memo = form.cleaned_data['memo']

                #Molding モデルを更新
                lot_number = self.object.lot_number
                molding = Molding.objects.filter(lot_number=lot_number).first()
                
                if molding:
                    # 既存のオブジェクトが存在する場合は更新
                    molding.good_molding = good_product
                    molding.bad_molding = bad_product
                    molding.user = user
                    molding.memo = memo
                    molding.save()


            if self.object.business.name == '検査':
                #stock モデルを更新するための情報を収集
                good_product = form.cleaned_data['good_product']
                user = form.cleaned_data['user']
                memo = form.cleaned_data['memo']
                
                #Stock モデルを更新
                lot_number = self.object.lot_number
                stocks = Stock.objects.filter(lot_number=lot_number).first()
                
                if stocks:
                    # 既存のオブジェクトが存在する場合は更新
                    stocks.stocks = good_product
                    stocks.inspection_user = user
                    stocks.memo = memo
                    stocks.save()
            
            return super().form_valid(form)

    
    
    

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

    
    #ShippingListViewのcontext_object_nameのデータを渡している。元々のShippingListViewではできないもよう
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        user_obj = self.request.user
        if user_obj.is_authenticated:
            context['shippings'] = Shipping.objects.filter(user=user_obj, created_at__date=today)
        else:
            context['shippings'] = []  

        context['user'] = user_obj
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

        #formで選択されたlot_numbeに合う値を取り出す
        molding_lot_number = form.cleaned_data['lot_number']
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


#在庫編集----------------------------------------------------------------------------------------------------------------------------------------------------------
class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = os.path.join('stock', 'stock_list.html')
    context_object_name = 'stocks'

    #製品ごとの合計を計算して表示する
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        grouped_stocks = Stock.objects.values('product__name').annotate(total_stocks=Sum('stocks'))

        context['grouped_stocks'] = grouped_stocks
        return context


class StockEditView(LoginRequiredMixin,UpdateView):
    model = Stock
    template_name = os.path.join('stock', 'stock_edit.html')
    form_class = StockEditForm
    success_url = reverse_lazy('daily_report:stock_list')

    
class StockDeleteView(LoginRequiredMixin,DeleteView):
    model = Stock
    template_name = os.path.join('stock', 'stock_delete.html')
    success_url = reverse_lazy('daily_report:stock_list')
    

#出荷編集----------------------------------------------------------------------------------------------------

class ShippingListView(LoginRequiredMixin, ListView):
    model = Shipping
    template_name = os.path.join('report', 'report_list.html')
    context_object_name = 'shippings'

    #ログインユーザーしか自分のデータを見ることができない設定
    def get_queryset(self):
        today = date.today()
        user_obj = self.request.user
        if user_obj.is_authenticated:
             qs = Shipping.objects.filter(user=user_obj,created_at__date = today)
        else:
            qs = Shipping.objects.none()
        return qs

    #ユーザーデータをテンプレートに渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #ユーザーデータ
        context['user'] = self.request.user
        return context

    
class ShippingDetailView(LoginRequiredMixin,DetailView):
    model = Shipping
    template_name = os.path.join('shipping', 'shipping_detail.html')
    context_object_name = 'shippingdetail'
            
class ShippingDeleteView(LoginRequiredMixin,DeleteView):
    model = Shipping
    success_url = reverse_lazy('daily_report:report_list')
    template_name = os.path.join('shipping', 'shipping_delete.html')


class ShippingStartView(LoginRequiredMixin,CreateView):
    model = Shipping
    form_class = ShippingStartForm
    template_name = os.path.join('shipping', 'shipping_start.html')
    success_url = reverse_lazy('daily_report:report_list')
    

    def form_valid(self, form):
        # フォームのバリデーションが成功した場合の処理
        form.instance.user = self.request.user
        cleaned_data = form.cleaned_data
        shipments_required = cleaned_data.get('shipments_required', 0)

        sets1 = cleaned_data.get('sets1', 0) or 0
        sets2 = cleaned_data.get('sets2', 0) or 0
        sets3 = cleaned_data.get('sets3', 0) or 0

        total = sets1 + sets2 + sets3

        error_occurred = False

        if shipments_required != total:
            form.add_error('sets1', '在庫選択し直してください')
            form.add_error('sets2', '在庫選択し直してください')
            form.add_error('sets3', '在庫選択し直してください')

            return self.form_invalid(form)
    
        
        #使用した数値から引いた数を在庫に導入する
        stock1 = cleaned_data.get('stock1')
        stock2 = cleaned_data.get('stock2')
        stock3 = cleaned_data.get('stock3')

        # 選択した在庫からセット数を引いて在庫を更新
        if stock1 is not None:
            new_stock1 = stock1.stocks - sets1
            if new_stock1 < 0:
                form.add_error('sets1', '在庫が足りません')
                error_occurred = True  # エラーが発生したことをマーク
            else:
                stock1.stocks = new_stock1
                stock1.save()


        if stock2 is not None:
            new_stock2 = stock2.stocks - sets2
            if new_stock2 < 0:
                form.add_error('sets2', '在庫が足りません')
                error_occurred = True  # エラーが発生したことをマーク
            else:
                stock2.stocks = new_stock2
                stock2.save()

        if stock3 is not None:
            new_stock3 = stock3.stocks - sets3
            if new_stock3 < 0:
                form.add_error('sets3', '在庫が足りません')
                error_occurred = True  # エラーが発生したことをマーク
            else:
                stock3.stocks = new_stock3
                stock3.save()

        if error_occurred:
            return self.form_invalid(form)
        
        business = Business.objects.get(name='出荷')
        lot_numbers = ':'.join([str(stock.lot_number) for stock in [stock1, stock2, stock3] if stock is not None])
        report_data = {
            'product': cleaned_data.get('product'),
            'user': self.request.user,
            'business': business,
            'lot_number': lot_numbers,
            'status': '終了',
            'good_product': cleaned_data.get('shipments_required'),
            'memo': cleaned_data.get('memo'),
        }
        report, created = Report.objects.get_or_create(**report_data)
    
        return super().form_valid(form)
    
    #フォームに初期値を渡す
    def get_initial(self):
        initial = super().get_initial()

        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # product_choices 変数をコンテキストに追加
        context['product_choices'] = Products.objects.all()
        
        return context
    
    
    #フォームにユーザー情報をわたし、部署ごとの業務内容を選択できるようにする。
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 

        return kwargs
    
    def get(self, request, *args, **kwargs):
        if 'product_id' in request.GET:
            product_id = request.GET['product_id']

            # ここで product_id を使用して必要な処理を実行する
            stock_options = self.get_stock_options(product_id)

            return JsonResponse(stock_options, safe=False)

        # GETパラメータに product_id がない場合、通常のビュー処理を実行
        return super().get(request, *args, **kwargs)
    
    def get_stock_options(self, product_id):
        try:
            # ここで product_id を使用して必要なデータを取得する処理を実行
            product = Products.objects.get(id=product_id)
            stock_options = Stock.objects.filter(product=product).values('id','created_at','product__name','lot_number','stocks')
            return list(stock_options)
        except Products.DoesNotExist:
            return []
    
    

   
#日報最終確認---------------------------------------------------------
class ReportLogoutConfirm(LoginRequiredMixin, ListView):
    model = Report
    template_name = os.path.join('logout.html')
    context_object_name = 'lastreports'


    #ログインユーザーしか自分のデータを見ることができない設定
    def get_queryset(self):
        today = date.today()
        user_obj = self.request.user
        if user_obj.is_authenticated:
             qs = Report.objects.filter(user=user_obj,created_at__date = today)
        else:
            qs = Report.objects.none()
        return qs