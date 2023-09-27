from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
# Create your views here.

from django.contrib.auth.views import LoginView, LogoutView

from .forms import LoginUserForm, RegistUserForm, StaffUserForm

from django.urls import reverse_lazy

from django.contrib.auth import login


class HomeView(TemplateView):
    template_name = 'home.html'
    
#ログイン
class LoginUserView(LoginView):
    template_name = 'login_user.html'
    authentication_form = LoginUserForm

    def get_success_url(self):
        user = self.request.user
        #staffという名のグループを検索し、existsでグループに入っているかいないかを確認する。
        if user.groups.filter(name='staff').exists():
            return reverse_lazy('product_management:staff_home')
        else:
            return super().get_success_url()

#入社登録
class RegistUserView(CreateView):
    template_name = 'regist_user.html'
    form_class = RegistUserForm
    success_url = reverse_lazy('accounts:login_user')

    #ログインしたのがstaffユーザーだったらstaff_homeにリダイレクトする
    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)

#staffユーザー作成
class StaffUserView(CreateView):
    form_class = StaffUserForm
    template_name = 'staff_user.html'  
    success_url = reverse_lazy('accounts:login_user')

    def form_valid(self, form):
        # フォームがバリデーションに成功した場合の処理
        user = form.save(commit=False)
        user.is_staff = form.cleaned_data['is_staff'] 
        user.save()
        return super().form_valid(form)
    

#ログアウト
class LogoutUserView(LogoutView):
    pass


  