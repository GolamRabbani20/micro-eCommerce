from django.contrib import admin
from .models import Product, ProductAttachment

@admin.register(Product)
class productAdmin(admin.ModelAdmin):
    list_display = ('pk','name', 'handle', 'price','orinal_price','timestamp','updated')
    


@admin.register(ProductAttachment)
class productAttachmentAdmin(admin.ModelAdmin):
    list_display = ('pk','file','name', 'product', 'is_free', 'updated')


