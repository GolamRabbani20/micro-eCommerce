from django.db import models
from django.conf import settings
from django.utils import timezone
import pathlib
from django.core.files.storage import FileSystemStorage
from django.urls import reverse

PROTECTED_MEDIA_ROOT = settings.PROTECTED_MEDIA_ROOT
protected_storage = FileSystemStorage(location=str(PROTECTED_MEDIA_ROOT))

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    # stripe_product_id = 
    image = models.ImageField(upload_to='product_img/', blank=True, null=True)
    name = models.CharField(max_length=120)
    handle = models.SlugField(unique=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2, default=9.99)
    orinal_price = models.DecimalField(max_digits=10, decimal_places=2, default=9.99)
    # stripe_price_id = 
    stripe_price = models.IntegerField(default=999) # 100 * price
    price_changed_timestamp = models.DateTimeField(auto_now=False, auto_now_add=True, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.price != self.orinal_price:
            self.orinal_price = self.price
            # trigger on API request for the price
            self.stripe_price = int(self.price * 100)
            self.price_changed_timestamp = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/products/{self.handle}/"
        # return reverse('products:detail', kwargs={'handle': self.handle})
    
    def get_manage_url(self):
        return f"/products/{self.handle}/manage/"

    def is_owner(self):
        return self.user.username

def handle_product_attatchment_upload(instance, filename):
    return f"products/{instance.product.handle}/attachments/{filename}"

class ProductAttachment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(upload_to=handle_product_attatchment_upload, storage=protected_storage)
    name = models.CharField(max_length=120, null=True, blank=True)
    is_free = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = pathlib.Path(self.file.name).name
        super().save(*args, **kwargs)
    
    @property
    def display_name(self):
        return self.name or pathlib.Path(self.file.name).name
    
    def get_download_url(self):
        url_kwargs = {'handle':self.product.handle, 'pk': self.pk }
        # return reverse("products: download", kwargs=url_kwargs )
        return f"/products/{self.product.handle}/download/{self.pk}/"
    
    def get_manage_url(self):
        return f"/products/{self.product.handle}/manage/"

