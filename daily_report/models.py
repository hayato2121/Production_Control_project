from django.db import models

# Create your models here.
from django.db import models
from accounts.models import Users, Departments


#製品情報
class Products(models.Model):
    name = models.CharField(max_length=255,verbose_name="製品名")
    code = models.CharField(max_length=50,verbose_name="製品コード")
    quantity = models.IntegerField(verbose_name="製品取り数")
    memo = models.CharField(max_length=255,blank=True, null=True,verbose_name="製品メモ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '製品情報'
        db_table = 'products'

    def __str__(self):
        return self.name + ':' + self.code 


#業務内容
class Business(models.Model):
    department = models.ForeignKey(
        Departments, on_delete=models.CASCADE, verbose_name='部署情報'
    )
    name = models.CharField(max_length=50,verbose_name="業務名")
    business_content = models.CharField(max_length=255,verbose_name="業務内容")

    class Meta:
        verbose_name = '業務内容'
        db_table = 'business'

    def __str__(self):
        return self.department.name + ':' + self.name



#日報テーブル
class Report(models.Model):
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE,verbose_name="ユーザー"
    )
    #製品情報紐付け
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE,verbose_name="製品情報"
    )
    #業務内容紐付け
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE,verbose_name="業務内容"
    )
    #ユーザー情報紐付け
    memo = models.CharField(max_length=255,blank=True, null=True,verbose_name="引き継ぎ",)
    lot_number = models.CharField(max_length=10, verbose_name='ロッド番号',default='')
    good_product= models.IntegerField(null=True,blank=True,verbose_name="優良数")
    bad_product= models.IntegerField(null=True,blank=True,verbose_name="不良数")
    status = models.CharField(max_length=10, null=True, blank=True, verbose_name="作業状況",)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '日報'
        db_table = "report"


    def __str__(self):
        return self.created_at.strftime('%Y-%m-%d') + ':' + self.user.username + ':' + self.product.name + ':' + self.lot_number + ':' + self.business.name

    