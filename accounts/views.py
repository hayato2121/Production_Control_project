from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
# Create your views here.

from django.contrib.auth.views import LoginView, LogoutView

from .forms import LoginUserForm, RegistUserForm, StaffUserForm

from django.contrib.auth.decorators import user_passes_test

from django.urls import reverse_lazy

from django.contrib.auth import login


class HomeView(TemplateView):
    template_name = 'home.html'
    
#ログイン
class LoginUserView(LoginView):
    template_name = 'login_user.html'
    authentication_form = LoginUserForm

#入社登録
class RegistUserView(CreateView):
    template_name = 'regist_user.html'
    form_class = RegistUserForm

    def form_valid(self, form):
        # フォームがバリデーションに成功した場合の処理
        user = form.save(commit=False)
        user.save()
        login(self.request, user)  # ユーザーをログインさせます
        return super().form_valid(form)

#staffユーザー作成
class StaffUserView(CreateView):
    form_class = StaffUserForm
    template_name = 'staff_user.html'  # 作成するテンプレートのパスを指定します
    success_url = reverse_lazy('product_management:staff_home')

    def form_valid(self, form):
        # フォームがバリデーションに成功した場合の処理
        user = form.save(commit=False)
        user.is_staff = form.cleaned_data['is_staff']  # フォームから is_staff フラグを取得して設定します
        user.save()
        login(self.request, user)  # ユーザーをログインさせます
        return super().form_valid(form)
    

#ログアウト
class LogoutUserView(LogoutView):
    pass


  