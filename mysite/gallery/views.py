from django.shortcuts import render
from django.core.paginator import Paginator
from .models import GalleryItem


def gallery_home(request):
    items_qs = GalleryItem.objects.filter(is_published=True)
    paginator = Paginator(items_qs, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    page_window_size = 3
    current_page = page_obj.number
    block_start = ((current_page - 1) // page_window_size) * page_window_size + 1
    block_end = min(block_start + page_window_size - 1, paginator.num_pages)
    page_numbers = list(range(block_start, block_end + 1))

    return render(request, 'gallery/gallery_list.html', {
        'items': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.paginator.num_pages > 1,
        'page_numbers': page_numbers,
        'first_page': 1,
        'last_page': paginator.num_pages,
        'previous_block_page': max(block_start - page_window_size, 1),
        'next_block_page': block_start + page_window_size if block_end < paginator.num_pages else paginator.num_pages,
        'has_previous_block': block_start > 1,
        'has_next_block': block_end < paginator.num_pages,
    })
