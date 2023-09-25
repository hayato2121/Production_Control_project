from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
# Create your views here.

from django.contrib.auth.views import LoginView, LogoutView

from .forms import LoginUserForm, RegistUserForm


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

#ログアウト
class LogoutUserView(LogoutView):
    pass

  