from django.db import models
from accounts.models import Users
from daily_report.models import Products
from datetime import datetime
# Create your models here.

#成形品---------------------------------------------------------------
class Molding(models.Model):
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, verbose_name='製品名'
    )
    lot_number = models.CharField(max_length=10, verbose_name='ロッド番号',default='')
    good_molding = models.IntegerField(verbose_name="優良成形数")
    bad_molding = models.IntegerField(verbose_name="不良成形数")
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, verbose_name='成形担当ユーザー名',null=True
    )
    memo = models.CharField(max_length=255,verbose_name="引き継ぎメモ",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '成形品'
        db_table = 'molding'

    def __str__(self):
        if self.user:
          return self.product.name + ':' + self.lot_number + ':' + self.user.username
        else:
          return self.product.name + ':' + self.lot_number + ':No User'
#納品先---------------------------------------------------------------
class Delivery(models.Model):
    delivery_name = models.CharField(max_length=50,verbose_name='納品先会社名')
    delivery_code = models.CharField(max_length=10,verbose_name='納品先コード')

    class Meta:
        verbose_name = '納品先'
        db_table = 'delivery'

    def __str__(self):
        return self.delivery_name


#在庫---------------------------------------------------------------
class Stock(models.Model):
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, verbose_name='製品名'
    )
    lot_number = models.CharField(max_length=10, verbose_name='ロッド番号',default='')
    stocks = models.IntegerField(verbose_name="在庫数")
    molding_user = models.ForeignKey(
        Users, on_delete=models.CASCADE, verbose_name='成形担当ユーザー名',null=True,related_name='molding_stock_set',
    )
    molding_time = models.DateTimeField(verbose_name='成形日時', default=datetime(2001, 1, 1, 0, 0, 0))
    inspection_user = models.ForeignKey(
        Users, on_delete=models.CASCADE, verbose_name='検査担当ユーザー名',null=True,related_name='inspection_stock_set',
    )
    memo = models.CharField(max_length=255,verbose_name="引き継ぎメモ",null=True,blank=True)
    created_at = models.DateTimeField(verbose_name='検査日時',auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '在庫'
        db_table = 'stock'

    def __str__(self):
        return '[' + self.created_at.strftime('%Y-%m-%d') + ']' + ':' + self.product.name + ':' + self.lot_number + ':' +'「' + '在庫数'+ '=' + '残り' + str(self.stocks) + '」'
#出荷---------------------------------------------------------------
class Shipping(models.Model):
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE,verbose_name='製品名',default=''
    )
    delivery = models.ForeignKey(
        Delivery, on_delete=models.CASCADE, verbose_name='納品先'
    )
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, verbose_name='作業者名',null=True
    )
    shipping_day = models.DateField(verbose_name='出荷日')
    shipments_required = models.IntegerField(verbose_name='出荷必要数')
    memo = models.CharField(max_length=255,verbose_name="引き継ぎメモ",null=True,blank=True)
    stock1 = models.ForeignKey(
        Stock, on_delete=models.CASCADE, verbose_name='使用在庫1',related_name='stock1_set',null=True
    )
    stock2 = models.ForeignKey(
        Stock, on_delete=models.CASCADE, verbose_name='使用在庫2',related_name='stock2_set',null=True
    )
    stock3 = models.ForeignKey(
        Stock, on_delete=models.CASCADE, verbose_name='使用在庫3',related_name='stock3_set',null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '出荷'
        db_table = 'shipping'

    def __str__(self):
        return str(self.delivery) + ':' + self.product.name + ':' + str(self.stock1) + ':' + str(self.stock2) + ':' + str(self.stock3) 


    