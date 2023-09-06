from django.shortcuts import render

from django.views.generic.list import ListView


#ログイン状態
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

#作業一覧
class WorkListView(LoginRequiredMixin, ListView):
    pass
