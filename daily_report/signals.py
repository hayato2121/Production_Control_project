from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Report
from product_management.models import Molding,Stock


# Report(成形)モデルが削除されたら自動的にMoldingオブジェクトを削除するシグナルハンドラ
@receiver(post_delete, sender=Report)
def delete_molding(sender, instance, **kwargs):
    # instanceは削除されたReportオブジェクト.reportの業務内容が成形の時だけ
    if instance.business.name == '成形':
        lot_number = instance.lot_number

        # Report.lot_numberと一致するMoldingオブジェクトを取得
        moldings = Molding.objects.filter(lot_number=lot_number)

        # すべてのMoldingオブジェクトを削除
        moldings.delete()

# Report(検査)モデルが削除されたら自動的にstockオブジェクトを削除するシグナルハンドラ
@receiver(post_delete, sender=Report)
def delete_stock(sender, instance, **kwargs):
    # instanceは削除されたReportオブジェクト.reportの業務内容が成形の時だけ
    if instance.business.name == '検査':
        lot_number = instance.lot_number

        # Report.lot_numberと一致するMoldingオブジェクトを取得
        stocks = Stock.objects.filter(lot_number=lot_number)

        # すべてのMoldingオブジェクトを削除
        stocks.delete()

@receiver(post_save, sender=Stock)
def update_molding(sender, instance, created, **kwargs):
    # Stock オブジェクトが作成された場合のみ処理を実行
    if created:
        lot_number = instance.lot_number

        # lot_number に一致する Molding オブジェクトを取得
        molding = Molding.objects.filter(lot_number=lot_number).first()

        if molding:
            # Molding オブジェクトを変更する必要がある場合の処理をここに記述
            # 例えば、以下のように Molding オブジェクトを更新する
            
            molding.delete()