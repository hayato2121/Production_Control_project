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
        fields = ['product', 'business']

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

        
        #詳細データからデータを引き出し初期値に登録
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

        #業務内容が検査の場合、good_productの初期値をgood_moldingから持ってくる
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
class ReportShippingEndForm(forms.ModelForm):
    product = forms.IntegerField(label='製品名')
    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.TextInput(attrs={'style': 'width: 200px; height: 100px;'}))

    class Meta:
        model = Shipping
        fields = ['product','user','delivery','shipping_day','shipments_required',
                  'stock1','stock2','stock3','memo']

    #初期値設定
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportShippingEndForm, self).__init__(*args, **kwargs)


        # 出荷部の人しか選べないようにする。
        if self.user and self.user.department.name == '出荷部':
            # 出荷部のユーザーのみを選択肢として表示
            self.fields['user'].queryset = Users.objects.filter(department__name='出荷部')
        else:
            # 出荷部のユーザーでない場合は何も表示しない
            self.fields['user'].queryset = Users.objects.none()

        #stock1,stock2,stock3の選択肢を選択した製品名の在庫だけにする
        product_id = self.initial.get('product')
        if product_id:
            #product_idを取得して、product_idをもとにnamaを取得してproductフィールドに保存する
            product = Products.objects.get(id=product_id)
            product_name = product.name + ':' + product.code
            self.fields['product'].initial = product_id
            self.product_name = product_name

            self.fields['stock1'].queryset = Stock.objects.filter(product = product)
            self.fields['stock2'].queryset = Stock.objects.filter(product = product)
            self.fields['stock3'].queryset = Stock.objects.filter(product = product)


        #初期値に設定したデータを編集できないようにする
        for field_name in [ 'product', 'user']:
            self.fields[field_name].widget.attrs['readonly'] = 'readonly'
    
    def clean(self):
        cleaned_data = super().clean()
        shipemnts_required = cleaned_data.get('shipments_required',0)
        stock1 = cleaned_data.get('stock1',0)
        stock2 = cleaned_data.get('stock2',0)
        stock3 = cleaned_data.get('stock3',0)

        total = stock1 + stock2 + stock3 

        if shipemnts_required != total:
            raise forms.ValidationError('在庫選択し直してください')
        
        return cleaned_data
