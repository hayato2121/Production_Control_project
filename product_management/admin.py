from django.contrib import admin

# Register your models here.
from .models import Molding,Delivery,Stock,Shipping

admin.site.register(
    [Molding,Delivery,Stock,Shipping]
)