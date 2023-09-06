from django.contrib import admin

# Register your models here.
from .models import Products,Business,Report

admin.site.register(
    [Products,Business,Report]
)