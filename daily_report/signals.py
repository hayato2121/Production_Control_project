from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Report
from product_management.models import Molding,Stock,Shipping

from accounts.models import Users
from django.contrib.auth.models import Group
from django.db.models import Q

from django.db.models import F, ExpressionWrapper, IntegerField,Value
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Concat




# Report(成形)モデルが削除されたら自動的にMoldingオブジェクトを削除するシグナルハンドラ----------------------------------
@receiver(post_delete, sender=Report)
def delete_molding(sender, instance, **kwargs):
    # instanceは削除されたReportオブジェクト.reportの業務内容が成形の時だけ
    if instance.business.name == '成形':
        lot_number = instance.lot_number

        # Report.lot_numberと一致するMoldingオブジェクトを取得
        moldings = Molding.objects.filter(lot_number=lot_number)

        # すべてのMoldingオブジェクトを削除
        moldings.delete()

# Report(検査)モデルが削除されたら自動的にstockオブジェクトを削除するシグナルハンドラ----------------------------------
@receiver(post_delete, sender=Report)
def delete_stock(sender, instance, **kwargs):
    # instanceは削除されたReportオブジェクト.reportの業務内容が成形の時だけ
    if instance.business.name == '検査':
        lot_number = instance.lot_number

        # Report.lot_numberと一致するMoldingオブジェクトを取得
        stocks = Stock.objects.filter(lot_number=lot_number)

        # すべてのMoldingオブジェクトを削除
        stocks.delete()

# Stockが作成した時に同じlot_numberのmoldingを消す----------------------------------
@receiver(post_save, sender=Stock)
def delete_related_molding(sender, instance, created, **kwargs):
    # Stock オブジェクトが作成された場合のみ処理を実行
    if created:
        lot_number = instance.lot_number

        # lot_number に一致する Molding オブジェクトを取得
        molding = Molding.objects.filter(lot_number=lot_number).first()

        if molding:
            # Molding オブジェクトが存在する場合にのみ削除
            molding.delete()
            
#shipping作成時に在庫が0になったら自動的に削除する----------------------------------
@receiver(post_save, sender=Stock)
def update_molding(sender, instance, **kwargs):
    
    if instance.stocks == 0:
        instance.delete()

#is_staffアカウントが作成されたら、自動でstaffグループに入れるシグナル
@receiver(post_save, sender=Users)
def staff_user_add_group(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        staff_group = Group.objects.get(name='staff')
        instance.groups.add(staff_group)

# shippingモデルが削除されたら自動的にreportオブジェクトを削除するシグナルハンドラ----------------------------------
@receiver(post_delete, sender=Shipping)
def delete_report(sender, instance, **kwargs):
    stock1 = instance.stock1
    stock2 = instance.stock2
    stock3 = instance.stock3

    # stock1, stock2, stock3 が None でないことを確認
    if stock1 is not None or stock2 is not None or stock3 is not None:
        lot_numbers = ':'.join(str(stock.lot_number) if stock is not None else '' for stock in [stock1, stock2, stock3])
        lot_numbers = ':'.join(filter(None, lot_numbers.split(':')))  # コロンを連続しないように修正
        print(lot_numbers)
        reports = Report.objects.filter(
            lot_number=lot_numbers,
            business__name='出荷',
        )
        reports.delete()
