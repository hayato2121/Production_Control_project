from django import forms

from .models import Report
from .models import Business,Products
from product_management.models import Molding, Shipping, Stock
from accounts.models import Users

from datetime import date
today = date.today()

from django.http import JsonResponse

#ランダム数値
import random 
import string

#--------------------------------------------------------------------------------------------------
class ReportStartForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ['product', 'business','good_product']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportStartForm, self).__init__(*args, **kwargs)
        
        if self.user and self.user.department:
            # ユーザーの部署と紐づく業務内容のみを選択肢として表示
            self.fields['business'].queryset = Business.objects.filter(department=self.user.department)


    #userフィールドに自動でリクエストユーザーをする。
    def save(self, commit=True):
        report = super(ReportStartForm, self).save(commit=False)
        if self.user:
            report.user = self.user

        #lot_numberにランダムの整数値を生成する.その時にreportモデルにあるlot_numberと被らないようにする。ユーザー部署が製造部の時だけ
        if self.user and self.user.department.name == '製造部':
            while True:
                random_value = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                if not Report.objects.filter(lot_number=random_value).exists():
                    report.lot_number = random_value
                    break

        if commit:
            report.save()
        return report

#--------------------------------------------------------------------------------------------------
class ReportEndForm(forms.ModelForm):
    product = forms.CharField(label='製品名')
    business = forms.CharField(label='業務内容')
    
    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.TextInput(attrs={'style': 'width: 200px; height: 100px;'}))
    sets = forms.IntegerField(label='セット数')
    bad_product = forms.IntegerField(label='不良数')
    quantity = forms.IntegerField(label='取り数', disabled=True)
    
    class Meta:
        model = Report
        fields = ['user','lot_number','quantity',
                  'sets','bad_product','memo']

    #初期値設定
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportEndForm, self).__init__(*args, **kwargs)


        # ユーザーの部署と紐づく業務内容のみを選択肢として表示
        if self.user and self.user.department:
            self.fields['business'].queryset = Business.objects.filter(department=self.user.department)
            self.fields['user'].queryset = Users.objects.filter(department=self.user.department)

        
        #下のread_onlyだけでは、forinkeyで紐付けされているフィールドは編集できてしまうので、
        #詳細データからデータを引き出し初期値に登録し、上でフィールドをcharfieldsにすることで
        #編集できなくし、データにも保存できる。
        if 'instance' in kwargs and kwargs['instance']:
            
            initial_data ={
                'product': kwargs['instance'].product,
                'business': kwargs['instance'].business,
                'user': kwargs['instance'].user,
                'lot_number': kwargs['instance'].lot_number,
                'quantity': kwargs['instance'].product.quantity
            }
            self.initial.update(initial_data)
        


        #初期値に設定したデータを編集できないようにする
        for field_name in [ 'product', 'business', 'user','lot_number']:
            self.fields[field_name].widget.attrs['readonly'] = 'readonly'

        #業務内容が成形以外なら成形数は入力しない
        if  self.instance and self.instance.business.name not in ('成形','検査'):
            self.fields['sets'].required = False
            self.fields['bad_product'].required = False
            self.fields['quantity'].required = False
            self.fields['sets'].widget = forms.HiddenInput()
            self.fields['bad_product'].widget = forms.HiddenInput()
            self.fields['quantity'].widget = forms.HiddenInput()

        #業務内容が検査の場合、good_productの初期値をgood_moldingから持ってくる。formの見た目を変えている。
        if self.instance and self.instance .business.name == '検査':
            lot_number = self.instance.lot_number
            try:
                molding = Molding.objects.get(lot_number = lot_number)
                good_molding = molding.good_molding
                self.initial['quantity'] = good_molding

                self.fields['quantity'].label = '成形優良数'
                del self.fields['sets']
            except Molding.DoesNotExist:
                self.add_error('good_product', '該当するデータが見つかりませんでした。')

    def clean_sets(self):
        sets = self.cleaned_data.get('sets')
        if sets is not None:
            if sets < 0:
                raise forms.ValidationError('負の値を入力できません')
            elif sets == 0:
                raise forms.ValidationError('0は入力できません.0を入力する場合は、日報ごと削除してください')
        return sets

    def clean_bad_product(self):
        bad_product = self.cleaned_data.get('bad_product')
        if bad_product is not None:
            if bad_product < 0:
                raise forms.ValidationError('負の値を入力できません')
        return bad_product
    

#--------------------------------------------------------------------------------------------------
class ReportStartInspectionForm(forms.ModelForm):
    lot_number = forms.ChoiceField(label='成形品ロッドナンバー', choices=[])

    class Meta:
        model = Report
        fields = ['lot_number','business']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportStartInspectionForm, self).__init__(*args, **kwargs)
        
        # Molding モデルから lot_number の値を取得して選択肢としてセットします

            # '検査部' の場合の条件を設定
        excluded_lot_numbers = Report.objects.filter(
            created_at__date=today,
            business__name='検査',  # '検査' という業務名に応じて調整
        ).values_list('lot_number', flat=True)
        
        all_molding_lot_numbers = Molding.objects.values_list('lot_number', flat=True).distinct()
        molding_lot_numbers = [lot_number for lot_number in all_molding_lot_numbers if lot_number not in excluded_lot_numbers]
        molding_choices = [(lot_number, lot_number) for lot_number in molding_lot_numbers]
        self.fields['lot_number'].choices = molding_choices

        #ユーザーの部署に合わせて業務内容を表示
        if self.user and self.user.department:
            self.fields['business'].queryset = Business.objects.filter(department=self.user.department)


    #userフィールドに自動でリクエストユーザーをする。
    def save(self, commit=True):
        report = super(ReportStartInspectionForm, self).save(commit=False)
        if self.user:
            report.user = self.user
        if commit:
            report.save()
        return report
    

    
#--------------------------------------------------------------------------------------------------
class ReportEndEditForm(forms.ModelForm):
    product = forms.CharField(label='製品名')
    business = forms.CharField(label='業務内容')
    bad_product = forms.IntegerField(label='不良数')
    good_product = forms.IntegerField(label='優良数')
    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.TextInput(attrs={'style': 'width: 200px; height: 100px;'}))
    
    class Meta:
        model = Report
        fields = ['user','lot_number','good_product',
                  'bad_product','memo']

    #初期値設定
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportEndEditForm, self).__init__(*args, **kwargs)


        # ユーザーの部署と紐づく業務内容のみを選択肢として表示
        if self.user and self.user.department:
            self.fields['business'].queryset = Business.objects.filter(department=self.user.department)
            self.fields['user'].queryset = Users.objects.filter(department=self.user.department)

        
        #詳細データからデータを引き出し初期値に登録
        if 'instance' in kwargs and kwargs['instance']:
            
            initial_data ={
                'product': kwargs['instance'].product,
                'business': kwargs['instance'].business,
                'user': kwargs['instance'].user,
                'lot_number': kwargs['instance'].lot_number,
                'good_product':kwargs['instance'].good_product,
                'bad_product':kwargs['instance'].bad_product,
                'memo': kwargs['instance'].memo
            }
            self.initial.update(initial_data)


        #初期値に設定したデータを編集できないようにする
        for field_name in [ 'product', 'business', 'user','lot_number']:
            self.fields[field_name].widget.attrs['readonly'] = 'readonly'

    def clean_good_product(self):
        good_product = self.cleaned_data.get('good_product')
        if good_product is not None:
            if good_product < 0:
                raise forms.ValidationError('負の値を入力できません')
            elif good_product == 0:
                raise forms.ValidationError('0は入力できません.0を入力する場合は、日報ごと削除してください')
        return good_product

    def clean_bad_product(self):
        bad_product = self.cleaned_data.get('bad_product')
        if bad_product is not None:
            if bad_product < 0:
                raise forms.ValidationError('負の値を入力できません')
        return bad_product
    


#-------------------------------------------------------------------------------------------------

class StockEditForm(forms.ModelForm):
    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.Textarea(attrs={'style': 'width: 200px; height: 100px; white-space:nomal;'}))
    stocks = forms.IntegerField(label='在庫数',required = False)
    class Meta:
        model = Stock
        fields = [ 'product','lot_number',
                  'molding_user','inspection_user',
                  'stocks','memo']
        
    def __init__(self, *args, **kwargs):
        super(StockEditForm, self).__init__(*args, **kwargs)


        for field_name in [ 'product','lot_number']:
            self.fields[field_name].widget.attrs['readonly'] = 'readonly'

        self.fields['molding_user'].queryset = Users.objects.filter(department__name='製造部')
        self.fields['inspection_user'].queryset = Users.objects.filter(department__name='検査部')
    
    #マイナスを入力できないようにする,０に入らないようにする,空白を無しにする
    def clean(self):
        stocks = self.cleaned_data.get('stocks')
        if stocks is not None:
            if stocks < 0:
                raise forms.ValidationError('負の値を入力できません')
            elif stocks == 0:
                raise forms.ValidationError('0は入力できません。在庫が0の場合は、削除ボタンを押して削除してください')

#-------------------------------------------------------------------------------------------------
class ShippingStartForm(forms.ModelForm):
    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.Textarea(attrs={'style': 'width: 200px; height: 100px; white-space:nomal;'}))
    sets1 = forms.IntegerField(label='在庫使用1',required = False)
    sets2 = forms.IntegerField(label='在庫使用2',required = False)
    sets3 = forms.IntegerField(label='在庫使用3',required = False)
    
    class Meta:
        model = Shipping
        fields = ['product','delivery','shipping_day','shipments_required',
                  'stock1','stock2','stock3','memo']
    
    #初期値設定
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ShippingStartForm, self).__init__(*args, **kwargs)

        self.fields['product'].queryset = Products.objects.all()

        #必須にしない
        self.fields['stock1'].required = False
        self.fields['stock2'].required = False
        self.fields['stock3'].required = False

    

    #マイナスを入力できないようにする,０に入らないようにする,空白を無しにする
    def clean_sets1(self):
        sets1 = self.cleaned_data.get('sets1')
        if sets1 is not None:
            if sets1 < 0:
                raise forms.ValidationError('負の値を入力できません')
            elif sets1 == 0:
                raise forms.ValidationError('0のままでは入力できません')
        return sets1
        
    def clean_sets2(self):
        sets2 = self.cleaned_data.get('sets2')
        if sets2 is not None:
            if sets2 < 0:
                raise forms.ValidationError('負の値を入力できません')
            elif sets2 == 0:
                raise forms.ValidationError('0のままでは入力できません')
        return sets2
    
    def clean_sets3(self):
        sets3 = self.cleaned_data.get('sets3')
        if sets3 is not None:
            if sets3 < 0:
                raise forms.ValidationError('負の値を入力できません')
            elif sets3 == 0:
                raise forms.ValidationError('0のままでは入力できません')
        return sets3
    
    def clean(self):
        cleaned_data = super().clean()
        stock1 = cleaned_data.get('stock1')
        stock2 = cleaned_data.get('stock2')
        stock3 = cleaned_data.get('stock3')

        # setsとstockのバリデーション
        for i in range(1, 4):
            sets_key = f'sets{i}'
            stock_key = f'stock{i}'
            sets = cleaned_data.get(sets_key)
            stock = cleaned_data.get(stock_key)

            if not sets and stock:
                self.add_error(sets_key, '在庫を入力し直してください')

                cleaned_data[sets_key] = None

            # 同じ在庫の選択を検証
        if stock1 and stock2 and stock1.id == stock2.id:
            self.add_error('stock2', '同じロッドナンバーの在庫を複数選択することはできません')

        if stock1 and stock3 and stock1.id == stock3.id:
            self.add_error('stock3', '同じロッドナンバーの在庫を複数選択することはできません')

        if stock2 and stock3 and stock2.id == stock3.id:
            self.add_error('stock3', '同じロッドナンバーの在庫を複数選択することはできません')

                
        return cleaned_data



