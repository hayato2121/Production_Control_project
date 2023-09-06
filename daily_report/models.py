from django.db import models

# Create your models here.
from django.db import models
from accounts.models import Users, Departments

#製品情報
class Products(models.Model):
    name = models.CharField(max_length=255,verbose_name="製品名")
    code = models.IntegerField(verbose_name="製品コード")
    quantity = models.IntegerField(verbose_name="製品取り数")
    pictures = models.FileField(upload_to='product_pictures/',verbose_name="製品画像")
    memo = models.CharField(max_length=255,blank=True, null=True,verbose_name="製品メモ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name


#業務内容
class Business(models.Model):
    department = models.ForeignKey(
        Departments, on_delete=models.CASCADE, verbose_name='部署情報'
    )
    name = models.CharField(max_length=50,verbose_name="業務名")
    business_content = models.CharField(max_length=255,verbose_name="業務内容")

    class Meta:
        db_table = 'business'

    def __str__(self):
        return self.name



#日報テーブル
class Report(models.Model):
    #製品情報紐付け
    product = models.ForeignKey(
        Products, on_delete=models.PROTECT,verbose_name="製品情報"
    )
    #業務内容紐付け
    busines = models.ForeignKey(
        Business, on_delete=models.PROTECT,verbose_name="業務内容"
    )
    #ユーザー情報紐付け
    user = models.ForeignKey(
        Users, on_delete=models.PROTECT,verbose_name="ユーザー"
    )
    operation_time = models.DateTimeField(null=True,blank=True, verbose_name="作業時間")
    good_product_total = models.IntegerField(null=True,blank=True,verbose_name="優良合計数")
    bad_product_total = models.IntegerField(null=True,blank=True,verbose_name="不良合計数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "report"

    def __str__(self):
        return self.user

