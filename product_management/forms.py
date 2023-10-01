from django import forms
from daily_report.models import Report,Products, Business
from product_management.models import Molding
from accounts.models import Users, Departments
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

    class Meta:
        model = Products
        fields = ['name', 'code' , 'quantity', 'memo']


#業務内容作成フォーム
class StaffBusinessCreateForm(forms.ModelForm):

    class Meta:
        model = Business
        fields = ['department', 'name' , 'business_content']


#日報編集フォーム
class StaffReportEditForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ['user','product','good_product','bad_product','status','memo']


#成形品編集フォーム
class StaffMoldingEditForm(forms.ModelForm):

    class Meta:
        model = Molding
        fields = ['product','lot_number','good_molding','bad_molding','user','memo']

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