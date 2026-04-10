from django.shortcuts import render

from .models import ServiceCategory


def services_home(request):
    categories = ServiceCategory.objects.prefetch_related('services').all()
    return render(request, 'services/services_list.html', {'categories': categories})
