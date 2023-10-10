from django.shortcuts import render, get_object_or_404
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
# Create your views here.

from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView,PasswordResetView,PasswordResetConfirmView

from django.views.generic.list import ListView
from django.views.generic.edit import (
    UpdateView, DeleteView, CreateView
)
from .forms import ProfileEditForm
from .models import Users

import os
from django.views import View

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from .forms import LoginUserForm, RegistUserForm, StaffUserForm, PasswordChangeForm,PasswordResetForm,SetPasswordForm

from django.urls import reverse_lazy



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

        # バリデーションエラーがある場合にはフォームを再描画し、エラーメッセージを表示
        try:
            user.save()
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    form.add_error(field, error)  # フォームのフィールドにエラーを追加

            return self.render_to_response(self.get_context_data(form=form))  # フォームを再描画
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

#ユーザー詳細画面
class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = os.path.join('user', 'profile.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
#ユーザー編集画面
class ProfileEditView(LoginRequiredMixin,UpdateView):
    model = Users
    form_class = ProfileEditForm
    template_name = os.path.join('user', 'profile_edit.html')
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user
    
#パスワード変更画面
class PasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = os.path.join('user','user_password_change.html')
    success_url = reverse_lazy('accounts:login_user')

    def form_valid(self, form):
        messages.success(self.request, 'パスワードが正常に変更されました。再度ログインしてください。')
        return super().form_valid(form)
    
#パスワードリセット
class PasswordResetView(PasswordResetView):
    subject_template_name = 'mail_template/password_reset/subject.txt'
    email_template_name = 'mail_template/password_reset/message.txt'
    template_name = os.path.join('user', 'user_password_reset.html')
    form_class = PasswordResetForm
    success_url = reverse_lazy('accounts:login_user')

    def form_valid(self, form):
        messages.success(self.request, 'パスワード再設定用のメールを送信しました。メールに記載されているリンクから再設定を行ってください。')
        return super().form_valid(form)

class PasswordResetConfirmView(PasswordResetConfirmView):
    
    form_class = SetPasswordForm
    success_url = reverse_lazy('accounts:login_user')
    template_name = os.path.join('user', 'user_password_confirm.html')

    def form_valid(self, form):
        messages.success(self.request, 'パスワード再設定を完了しました')
        return super().form_valid(form)



#ログアウト
class LogoutUserView(LogoutView):
    pass

