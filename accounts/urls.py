from django.urls import path
from .views import HomeView, LoginUserView, RegistUserView, LogoutUserView

app_name = 'accounts'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    #ログイン
    path('login_user/', LoginUserView.as_view(), name='login_user'),
    #入社登録
    path('regist_user/', RegistUserView.as_view(), name='regist_user'),
    #ログアウト
    path('logout_user/', LogoutUserView.as_view(), name='logout_user'),
]