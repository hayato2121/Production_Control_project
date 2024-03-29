from django import forms
from daily_report.models import Report,Products, Business
from product_management.models import Molding
from accounts.models import Users, Departments
from .models import Stock
from django.contrib.auth.password_validation import validate_password


#年と月の選択肢
YEAR_CHOICES = [(year, str(year)) for year in range(2020, 2026)]  # 2020年から2030年までの範囲を選択肢にする例

MONTH_CHOICES = [
    (1, '1月'), (2, '2月'), (3, '3月'), (4, '4月'),
    (5, '5月'), (6, '6月'), (7, '7月'), (8, '8月'),
    (9, '9月'), (10, '10月'), (11, '11月'), (12, '12月')
]

#グラフに渡す年と月を入力するフォーム
class GraphYearMonthForm(forms.Form):
    year = forms.ChoiceField(choices=YEAR_CHOICES, label='年')
    month = forms.ChoiceField(choices=MONTH_CHOICES, label='月')


#製品作成フォーム
class StaffProductCreateForm(forms.ModelForm):

    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.Textarea(attrs={'style': 'width: 200px; height: 100px; white-space:nomal;'}))

    class Meta:
        model = Products
        fields = ['name', 'code' , 'quantity', 'memo']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None:
            if quantity < 0:
                raise forms.ValidationError('負の値を入力できません')
            elif quantity == 0:
                raise forms.ValidationError('0は入力できません.0を入力する場合は、削除してください')
        return quantity

    

#製品編集フォーム
class StaffProductEditForm(forms.ModelForm):

    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.Textarea(attrs={'style': 'width: 200px; height: 100px; white-space:nomal;'}))

    class Meta:
        model = Products
        fields = ['name', 'code' , 'quantity', 'memo']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None:
            if quantity < 0:
                raise forms.ValidationError('負の値を入力できません')
            elif quantity == 0:
                raise forms.ValidationError('0は入力できません.0を入力する場合は、削除してください')
        return quantity


#業務内容作成フォーム
class StaffBusinessCreateForm(forms.ModelForm):
    business_content = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.Textarea(attrs={'style': 'width: 200px; height: 100px; white-space:nomal;'}))

    class Meta:
        model = Business
        fields = ['department', 'name' , 'business_content']


#日報編集フォーム
class StaffReportEditForm(forms.ModelForm):

    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.Textarea(attrs={'style': 'width: 200px; height: 100px; white-space:nomal;'}))

    class Meta:
        model = Report
        fields = ['user','product','good_product','bad_product','status','memo']

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


#成形品編集フォーム
class StaffMoldingEditForm(forms.ModelForm):

    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.Textarea(attrs={'style': 'width: 200px; height: 100px; white-space:nomal;'}))


    class Meta:
        model = Molding
        fields = ['product','lot_number','good_molding','bad_molding','user','memo']

    def clean_good_molding(self):
        good_molding = self.cleaned_data.get('good_molding')
        if good_molding is not None:
            if good_molding < 0:
                raise forms.ValidationError('負の値を入力できません')
            elif good_molding == 0:
                raise forms.ValidationError('0は入力できません.0を入力する場合は、削除してください')
        return good_molding

    def clean_badmolding(self):
        bad_molding = self.cleaned_data.get('bad_molding')
        if bad_molding is not None:
            if bad_molding < 0:
                raise forms.ValidationError('負の値を入力できません')
        return bad_molding   

#user編集フォーム
class StaffUserEditForm(forms.ModelForm):

    username = forms.CharField(label='名前',widget=forms.TextInput(attrs={'placeholder': '間の空白なし[山田太郎]'}))
    birthday = forms.DateField(label='生年月日',widget=forms.TextInput(attrs={'placeholder': '2000-01-01'}))
    phone = forms.IntegerField(label='緊急連絡先番号',required=True,widget=forms.TextInput(attrs={'placeholder': 'ハイフンなしで入力してください'}))
    email = forms.EmailField(label='連絡先メールアドレス',required=True,widget=forms.TextInput(attrs={'placeholder': 'your_email@example.com'}))
    department = forms.ModelChoiceField(queryset=Departments.objects,
        label='所属部署', 
        required=True,)
    password = forms.CharField(label='パスワード',widget=forms.PasswordInput())

    class Meta:
        model = Users
        fields = ('username', 'birthday','phone', 'email', 'department')

    #パスワードの暗号化
    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'],user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user
    
class StaffStockEditForm(forms.ModelForm):

    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.Textarea(attrs={'style': 'width: 200px; height: 100px; white-space:nomal;'}))
    stocks = forms.IntegerField(label='在庫数',required = False)
    class Meta:
        model = Stock
        fields = [ 'product','lot_number',
                  'molding_user','inspection_user',
                  'stocks','memo']
        
    def __init__(self, *args, **kwargs):
        super(StaffStockEditForm, self).__init__(*args, **kwargs)


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
        
    