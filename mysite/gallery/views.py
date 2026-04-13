from django.shortcuts import render
from django.core.paginator import Paginator
from .models import GalleryItem


def gallery_home(request):
    items_qs = GalleryItem.objects.filter(is_published=True)
    paginator = Paginator(items_qs, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'gallery/gallery_list.html', {
        'items': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.paginator.num_pages > 1,
    })
