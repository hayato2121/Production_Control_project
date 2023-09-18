from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Report
from product_management.models import Molding


# Reportモデルが削除されたら自動的にMoldingオブジェクトを削除するシグナルハンドラ
@receiver(post_delete, sender=Report)
def delete_molding(sender, instance, **kwargs):
    # instanceは削除されたReportオブジェクト
    lot_number = instance.lot_number

    # Report.lot_numberと一致するMoldingオブジェクトを取得
    moldings = Molding.objects.filter(lot_number=lot_number)

    # すべてのMoldingオブジェクトを削除
    moldings.delete()
