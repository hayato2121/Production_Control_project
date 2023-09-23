from django.contrib import admin

# Register your models here.
from .models import Molding,Delivery,Stock,Shipping

class StockAdmin(admin.ModelAdmin):
    fields = ['product', 'lot_number', 'stocks', 'molding_user','molding_time',
               'inspection_user','created_at', 'memo']
    readonly_fields = ['created_at']

admin.site.register(Molding)
admin.site.register(Delivery)
admin.site.register(Stock,StockAdmin)
admin.site.register(Shipping)