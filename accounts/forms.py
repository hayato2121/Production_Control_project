from django import forms
from .models import Users, Departments
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth.forms import AuthenticationForm ,PasswordChangeForm,PasswordResetForm, SetPasswordForm

from django.contrib.auth.hashers import make_password

#ログイン
class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='名前')
    password = forms.CharField(label='パスワード',widget=forms.PasswordInput())

#入社登録
class RegistUserForm(forms.ModelForm):
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
    

#staffuser作成
class StaffUserForm(RegistUserForm):

    is_staff = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='管理者'
    )

    class Meta:
        model = Users
        fields = RegistUserForm.Meta.fields + ('is_staff',)

    #パスワードの暗号化
    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'],user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user
    

#ユーザー編集画面
class ProfileEditForm(forms.ModelForm):
    password = forms.CharField(label='現行パスワード', widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(label='現行パスワード（確認）', widget=forms.PasswordInput, required=True)

    class Meta:
        model = Users
        fields = ('username', 'email', 'phone', 'department')

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        # 新しいパスワードと確認用パスワードが一致しない場合、エラーメッセージを表示
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('パスワードと確認用パスワードが一致しません。')
        
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.password = make_password(password)

        if commit:
            user.save()
        
        return user
    
#パスワード変更
class PasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


#パスワードリセットフォーム
class PasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#パスワード再設定用フォーム
class SetPasswordForm(SetPasswordForm):
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)