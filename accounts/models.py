from django.db import models

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)

from django.urls import reverse_lazy

# Create your models here.

#部署テーブル---------------------------------------------------------------------------

class Departments(models.Model):
    name = models.CharField(max_length=50, verbose_name="部署")

    class Meta:
        verbose_name = '部署'
        db_table = 'departments'

    def __str__(self):
        return self.name

#ユーザーテーブルマネージャー---------------------------------------------------------------
class UsersManager(BaseUserManager):
    #ユーザー作成手法
    def create_user(self, username, email, password=True):
        if not email:
            raise ValueError('emailを入力してください')
        user = self.model(
            username = username,
            email = email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,username, email, password=True):
        user = self.model(
            username = username,
            email = email,
        )
        user.set_password(password)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    
    


# ユーザーテーブル---------------------------------------------------------------
class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, verbose_name="ユーザー名")
    birthday = models.DateField(null=True,blank=True, verbose_name="生年月日")
    phone = models.CharField(max_length=11,null=True,blank=True, verbose_name="携帯番号")
    email = models.EmailField(max_length=255, unique=True, verbose_name="メールアドレス")
    #部署テーブルとの紐付け
    department = models.ForeignKey(
        Departments, on_delete=models.PROTECT, null=True,blank=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    objects = UsersManager()

    def get_absolute_url(self):
        return reverse_lazy('accounts:home')
