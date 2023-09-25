from django import forms

from .models import Report
from .models import Business,Products
from product_management.models import Molding, Shipping, Stock
from accounts.models import Users

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


#--------------------------------------------------------------------------------------------------
class ReportStartInspectionForm(forms.ModelForm):
    molding_lot_number = forms.ChoiceField(label='成形品ロッドナンバー', choices=[])

    class Meta:
        model = Report
        fields = ['molding_lot_number','business']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportStartInspectionForm, self).__init__(*args, **kwargs)

        # Molding モデルから lot_number の値を取得して選択肢としてセットします
        molding_lot_numbers = Molding.objects.values_list('lot_number', flat=True).distinct()
        molding_choices = [(lot_number, lot_number) for lot_number in molding_lot_numbers] #unique_molding_lot_number]
        self.fields['molding_lot_number'].choices = molding_choices

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
class ShippingStartForm(forms.ModelForm):

    class Meta:
        model = Shipping
        fields = ['product', 'delivery','shipping_day','shipments_required']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ShippingStartForm, self).__init__(*args, **kwargs)
        
    #userフィールドに自動でリクエストユーザーをする。
    def save(self, commit=True):
        shipping = super(ShippingStartForm, self).save(commit=False)
        if self.user:
            shipping.user = self.user
        if commit:
            shipping.save()
        return shipping

        
#--------------------------------------------------------------------------------------------------
class ReportShippingEndForm(forms.ModelForm):
    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.TextInput(attrs={'style': 'width: 200px; height: 100px;'}))
    sets1 = forms.IntegerField(label='在庫使用1',required = False)
    sets2 = forms.IntegerField(label='在庫使用2',required = False)
    sets3 = forms.IntegerField(label='在庫使用3',required = False)

    class Meta:
        model = Shipping
        fields = ['product','user','delivery','shipping_day','shipments_required',
                  'stock1','stock2','stock3','memo']

    #初期値設定
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportShippingEndForm, self).__init__(*args, **kwargs)

        self.fields['stock1'].required = False
        self.fields['stock2'].required = False
        self.fields['stock3'].required = False

        # 出荷部の人しか選べないようにする。
        if self.user and self.user.department.name == '出荷部':
            # 出荷部のユーザーのみを選択肢として表示
            self.fields['user'].queryset = Users.objects.filter(department__name='出荷部')
        else:
            # 出荷部のユーザーでない場合は何も表示しない
            self.fields['user'].queryset = Users.objects.none()


        #stock1,stock2,stock3の選択肢を選択した製品名の在庫だけにする
        product  = self.initial.get('product')
        if product:
            #product_idを取得して、product_idをもとにnamaを取得してproductフィールドに保存する
            self.fields['stock1'].queryset = Stock.objects.filter(product = product)
            self.fields['stock2'].queryset = Stock.objects.filter(product = product)
            self.fields['stock3'].queryset = Stock.objects.filter(product = product)


        #初期値に設定したデータを編集できないようにする
        for field_name in [ 'product', 'user']:
            self.fields[field_name].widget.attrs['readonly'] = 'readonly'

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


#-------------------------------------------------------------------------------------------------

class ReportShippingEndEditForm(forms.ModelForm):
    
    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.TextInput(attrs={'style': 'width: 200px; height: 100px;'}))
    
    class Meta:
        model = Shipping
        fields = ['product','user','delivery','shipping_day','shipments_required',
                  'stock1','stock2','stock3','memo']
    
    
    #初期値設定
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportShippingEndEditForm, self).__init__(*args, **kwargs)


        # ユーザーの部署と紐づく業務内容のみを選択肢として表示
        if self.user and self.user.department:
            self.fields['user'].queryset = Users.objects.filter(department=self.user.department)

        
        #詳細データからデータを引き出し初期値に登録
        if 'instance' in kwargs and kwargs['instance']:
            
            initial_data ={
                'product': kwargs['instance'].product,
                'user': kwargs['instance'].user,
                'delivery': kwargs['instance'].delivery,
                'shipping_day': kwargs['instance'].shipping_day,
                'shipments_required': kwargs['instance'].shipments_required,
                'stock1': kwargs['instance'].stock1,
                'stock2': kwargs['instance'].stock2,
                'stock3': kwargs['instance'].stock3,
                'memo': kwargs['instance'].memo
            }
            self.initial.update(initial_data)

#-------------------------------------------------------------------------------------------------

class StockEditForm(forms.ModelForm):

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


#-------------------------------------------------------------------------------------------------
class ShippingEndForm(forms.ModelForm):
    product = forms.CharField(label='製品名')
    delivery = forms.CharField(label='納品先')
    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.TextInput(attrs={'style': 'width: 200px; height: 100px;'}))
    sets1 = forms.IntegerField(label='在庫使用1',required = False)
    sets2 = forms.IntegerField(label='在庫使用2',required = False)
    sets3 = forms.IntegerField(label='在庫使用3',required = False)
    
    class Meta:
        model = Shipping
        fields = ['user','shipping_day','shipments_required',
                  'stock1','stock2','stock3','memo']
    
    #初期値設定
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ShippingEndForm, self).__init__(*args, **kwargs)

        #必須にしない
        self.fields['stock1'].required = False
        self.fields['stock2'].required = False
        self.fields['stock3'].required = False

        # ユーザーの部署と紐づく業務内容のみを選択肢として表示
        if self.user and self.user.department:
            self.fields['user'].queryset = Users.objects.filter(department=self.user.department)


        #下のread_onlyだけでは、forinkeyで紐付けされているフィールドは編集できてしまうので、
        #詳細データからデータを引き出し初期値に登録し、上でフィールドをcharfieldsにすることで
        #編集できなくし、データにも保存できる。
        if 'instance' in kwargs and kwargs['instance']:
            
            initial_data ={
                'product': kwargs['instance'].product,
                'delivery': kwargs['instance'].delivery,
            }
            self.initial.update(initial_data)

        # 製品フィールドから選択された製品を取得
        selected_product = self.initial.get('product')
        # 製品に関連する在庫オブジェクトをクエリして取得し、選択肢として設定
        if selected_product:
            self.fields['stock1'].queryset = Stock.objects.filter(product=selected_product)
            self.fields['stock2'].queryset = Stock.objects.filter(product=selected_product)
            self.fields['stock3'].queryset = Stock.objects.filter(product=selected_product)
       
        #初期値に設定したデータを編集できないようにする
        for field_name in [ 'product','delivery','shipping_day','shipments_required',]:
            self.fields[field_name].widget.attrs['readonly'] = 'readonly'

            


