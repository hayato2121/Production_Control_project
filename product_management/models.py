from django.db import models
from accounts.models import Users
from daily_report.models import Products
# Create your models here.

#成形品作成---------------------------------------------------------------
class Molding(models.Model):
    user = models.ForeignKey(
        Users, on_delete=models.PROTECT, verbose_name='ユーザー名'
    )
    product = models.ForeignKey(
        Products, on_delete=models.PROTECT, verbose_name='製品名'
    )
    lot_number = models.IntegerField(verbose_name="ロッドナンバー")
    good_molding = models.IntegerField(verbose_name="優良成形数")
    bat_molding = models.IntegerField(verbose_name="不良成形数")
    memo = models.CharField(max_length=255,verbose_name="成形メモ",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'molding'

    def __str__(self):
        return self.product + ':' + self.user + ':' + self.lot_number

    
#納品先---------------------------------------------------------------
class Delivery(models.Model):
    delivery_name = models.CharField(max_length=50,verbose_name='納品先会社名')
    delivery_code = models.IntegerField(verbose_name='納品先コード')

    class Meta:
        db_table = 'delivery'

    def __str__(self):
        return self.delivery_name


#在庫---------------------------------------------------------------
class Stock(models.Model):
    molding = models.OneToOneField(
        Molding, on_delete=models.PROTECT, primary_key=True,verbose_name="成形品情報"
    )
    total = models.IntegerField(verbose_name="製品合計数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stock'


#出荷
class Shipping(models.Model):
    stock = models.ForeignKey(
        Stock, on_delete=models.PROTECT, verbose_name='在庫情報'
    )
    delivery = models.ForeignKey(
        Delivery, on_delete=models.PROTECT, verbose_name='納品先情報'
    )
    shipping_day = models.DateField(verbose_name='出荷日')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shipping'



    