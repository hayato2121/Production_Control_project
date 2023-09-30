from typing import Any
from django.shortcuts import render
from django.views import View

from accounts.models import Users
from daily_report.models import Report, Products

from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView
from django.views import View

import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.db.models import Sum
import io
import base64
import numpy as np


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
 


#日報の集計グラフ
class StaffReportUserGraphView(View):
    template_name = os.path.join('staff', 'staff_reportusergraph.html')

    def get(self, request, *args, **kwargs):

        users = Users.objects.filter(department__name='製造部')
        products = Products.objects.all()

        user_data = {}  # ユーザーごとのデータを格納する辞書

        for user in users:
            user_data[user.username] = {product.name: 0 for product in products}

        for product in products:
            product_good_data = Report.objects.filter(product=product).values('user__username').annotate(total_good_product=Sum('good_product'))
            for entry in product_good_data:
                username = entry['user__username']
                total_good_product = entry['total_good_product'] or 0
                if username in user_data:
                    user_data[username][product.name] = total_good_product

        # グラフにデータを設定
        labels = [user.username for user in users]
        x = range(len(users))

        # グラフ描写
        plt.figure(figsize=(12, 6))

        plt.ylim(0, 100000) #y軸のラベルの範囲を指定0から1000000

        # ユーザごとにデータを積み上げて描写
        bottom_data = np.zeros(len(users), dtype=float)
        for product in products:
            product_good_data = [user_data[user.username][product.name] for user in users]
            plt.bar(x, product_good_data, label=product.name, bottom=bottom_data)
            bottom_data += product_good_data


        plt.xlabel('ユーザー',)
        plt.ylabel('優良数',)
        plt.xticks(x, labels, rotation=45)
        plt.tight_layout()
        plt.legend(prop = {'family' : 'IPAexGothic'})

        # グラフを画像ファイルとして保存
        image_stream = io.BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)
        image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')
        plt.close()

        context = {
            'chart_image': image_base64,
        }

        return render(request, self.template_name, context)