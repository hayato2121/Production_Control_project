from django.urls import path
from .views import (
     HomeView, LoginUserView, RegistUserView, LogoutUserView,StaffUserView,
     ProfileView, ProfileEditView
)

app_name = 'accounts'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('login_user/', LoginUserView.as_view(), name='login_user'),
    path('regist_user/', RegistUserView.as_view(), name='regist_user'),
    path('staff_user/', StaffUserView.as_view(), name='staff_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/edit/', ProfileEditView.as_view(),name='profile_edit'),
    path('logout_user/', LogoutUserView.as_view(), name='logout_user'),

]