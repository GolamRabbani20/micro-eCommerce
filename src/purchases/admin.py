from django.contrib import admin
from .models import purchasesProduct

@admin.register(purchasesProduct)
class purchasesProductAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'product', 'completed', 'stripe_price', 'timestamp')
