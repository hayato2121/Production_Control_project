from typing import Any
from django.shortcuts import render
from django.views import View

from accounts.models import Users

from django.contrib.auth.decorators import login_required

from django.views.generic.list import ListView
from django.views.generic import TemplateView

import os
#staffユーザーしかアクセスできない

#ログインしているユーザーを取得する。
@login_required
def employee_attendance(request):
    login_user = request.user
    attendance_info = login_user.attendance

    return render(request, 'staff_home.html', {'logged_in_user': login_user, 'attendance_info': attendance_info})

#上で取得したユーザー情報をリストとして表示する。
class StaffHomeView(TemplateView):
    model = Users
    template_name = os.path.join('staff', 'staff_home.html')
    context_object_name = 'users'

   #部署ごとにログインユーザーを取得する
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #ユーザーがログインしているか確認
        if self.request.user.is_authenticated:
            # ログインしているユーザーの部署を取得
            login_user = self.request.user
            department_user = login_user.department.name

        # ログインユーザーの部署に基づいてユーザー情報を取得
            department_users = Users.objects.filter(department__name=department_user)

            context['department_users'] = department_users

        return context
 