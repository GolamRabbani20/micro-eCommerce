import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductAttachment
from purchases.models import purchasesProduct
from .forms import ProductForm, ProductUpdateForm, ProductAttachmentInlinelFormset
from django.http import FileResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse

import boto3
from django.conf import settings
from home.storages.utils import generate_presigned_url

def product_create_view(request):
    if request.method == 'POST' and 'image' in request.FILES:
        file = request.FILES['image']
        # Initialize the S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        # Upload the file
        s3.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file.name,
            ExtraArgs={'ContentType': file.content_type}  # Preserve content type
        )

    user = request.user
    form = ProductForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        if user.is_authenticated:
            obj.user = user
            obj.save()
            return redirect(obj.get_absolute_url('list'))
        form.add_error(None,'You must be logged in to create product!')
    return render(request, 'products/create.html', {'form': form})

def product_list_view(request):
    product_objects = Product.objects.all()
    return render(request, 'products/list.html', {'product_objects': product_objects})

def product_manage_detail_view(request, handle=None):
    obj = get_object_or_404(Product, handle=handle)
    attachments = ProductAttachment.objects.filter(product=obj)
    context = {}
    context['object'] = obj
    is_manager = False
    if request.user.is_authenticated:
        is_manager = obj.user == request.user
        
    if not is_manager:
        return HttpResponseBadRequest()
    form = ProductUpdateForm(request.POST or None, request.FILES or None, instance=obj)
    formset = ProductAttachmentInlinelFormset(request.POST or None, request.FILES or None, queryset=attachments)

    if form.is_valid() and formset.is_valid():
        instance = form.save(commit=False)
        instance.save()
        formset.save(commit=False)
        for _form in formset:
            is_delete = _form.cleaned_data.get('DELETE')
            print(is_delete)
            try:
                attachment_obj = _form.save(commit=False)
            except:
                attachment_obj = None
            if is_delete:
                if attachment_obj is not None:
                    if attachment_obj.pk:
                        attachment_obj.delete()
            else:
                if attachment_obj is not None:
                    attachment_obj.product = instance
                    attachment_obj.save()
        return redirect(obj.get_absolute_url())
    context['form'] = form
    context['formset'] = formset
    return render(request, 'products/manager.html', context)

def product_detail_view(request, handle=None):
    obj = get_object_or_404(Product, handle=handle)
    attachments = ProductAttachment.objects.filter(product=obj)
    # attachments = obj.productattachment_set.all() # it's a property of foreginkey
    # print(obj.user, request.user)
    is_owner=False
    if request.user.is_authenticated and obj.user == request.user:
        is_owner = True
        # is_owner = request.user.purchasesproduct_set.all().filter(product=obj, completed=True).exists()
        
    can_access = True if request.user.is_authenticated else False

    context = {'object': obj,'is_owner': is_owner, 'attachments': attachments, 'can_access': can_access}
    return render(request, 'products/detail.html', context)

def product_attachment_download_view(request, handle=None, pk=None):
    attachment = get_object_or_404(ProductAttachment, product__handle=handle, pk=pk)
    can_download = attachment.is_free or False
    can_download = True if request.user.is_authenticated else False
    if request.user.is_authenticated and can_download is False:
        can_download = request.user.purchasesproduct_set.all().filter(product=attachment.product, completed=True).exists()
    if can_download is False:
        return HttpResponseBadRequest()
    file_name = attachment.file.name  #.open(mode='rb') #readbyte
    file_url = generate_presigned_url(file_name)
    # filename = attachment.file.name
    # content_type, _ = mimetypes.guess_type(filename)
    # response = FileResponse(file)
    # response['Conten-Type'] = content_type or 'application/octet-stream'
    # response['Content-Disposition'] = f'attachment;filename={filename}'
    return HttpResponseRedirect(file_url)


