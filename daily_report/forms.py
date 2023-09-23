from django import forms

from .models import Report
from .models import Business
from product_management.models import Molding
from accounts.models import Users

#ランダム数値
import random 
import string

#--------------------------------------------------------------------------------------------------
class ReportStartForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ('product', 'business')

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

        #lot_numberにランダムの整数値を生成する.その時にreportモデルにあるlot_numberと被らないようにする
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
        molding_choices = [(lot_number, lot_number) for lot_number in molding_lot_numbers]
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
        
