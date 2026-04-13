from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import ServiceCategoryForm, ServiceForm
from .models import Service, ServiceCategory


def _can_manage(request):
    """Return True if user is admin, manager, staff, or superuser."""
    if not request.user.is_authenticated:
        return False
    if request.user.is_staff or request.user.is_superuser:
        return True
    profile = getattr(request.user, 'profile', None)
    return profile is not None and profile.role in ('admin', 'manager')


def services_home(request):
    categories = ServiceCategory.objects.prefetch_related('services').all()
    return render(request, 'services/services_list.html', {'categories': categories})


@login_required
def category_list(request):
    if not _can_manage(request):
        messages.error(request, _("Neturite teisės pasiekti šio puslapio."))
        return redirect('services_home')

    q = request.GET.get('q', '').strip()
    categories = ServiceCategory.objects.all()
    if q:
        categories = categories.filter(name__icontains=q)

    return render(request, 'services/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if not _can_manage(request):
        messages.error(request, _("Neturite teisės pasiekti šio puslapio."))
        return redirect('services_home')

    form = ServiceCategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _("Kategorija sukurta."))
        return redirect('category_list')

    return render(request, 'services/category_form.html', {'form': form})


@login_required
def category_edit(request, pk):
    if not _can_manage(request):
        messages.error(request, _("Neturite teisės pasiekti šio puslapio."))
        return redirect('services_home')

    category = get_object_or_404(ServiceCategory, pk=pk)
    form = ServiceCategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _("Kategorija atnaujinta."))
        return redirect('category_list')

    return render(request, 'services/category_form.html', {'form': form})


@login_required
def category_delete(request, pk):
    if not _can_manage(request):
        messages.error(request, _("Neturite teisės pasiekti šio puslapio."))
        return redirect('services_home')

    category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, _("Kategorija ištrinta."))
        return redirect('category_list')

    return render(
        request,
        'services/confirm_delete.html',
        {'object': category, 'object_type': _('kategorija'), 'cancel_url': 'category_list'},
    )


@login_required
def service_list(request):
    if not _can_manage(request):
        messages.error(request, _("Neturite teisės pasiekti šio puslapio."))
        return redirect('services_home')

    q = request.GET.get('q', '').strip()
    services = Service.objects.select_related('category').all()
    if q:
        services = services.filter(Q(name__icontains=q) | Q(category__name__icontains=q)).distinct()

    return render(request, 'services/service_list.html', {'services': services})


@login_required
def service_create(request):
    if not _can_manage(request):
        messages.error(request, _("Neturite teisės pasiekti šio puslapio."))
        return redirect('services_home')

    form = ServiceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _("Paslauga sukurta."))
        return redirect('service_list')

    return render(request, 'services/service_form.html', {'form': form})


@login_required
def service_edit(request, pk):
    if not _can_manage(request):
        messages.error(request, _("Neturite teisės pasiekti šio puslapio."))
        return redirect('services_home')

    service = get_object_or_404(Service, pk=pk)
    form = ServiceForm(request.POST or None, instance=service)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _("Paslauga atnaujinta."))
        return redirect('service_list')

    return render(request, 'services/service_form.html', {'form': form})


@login_required
def service_delete(request, pk):
    if not _can_manage(request):
        messages.error(request, _("Neturite teisės pasiekti šio puslapio."))
        return redirect('services_home')

    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, _("Paslauga ištrinta."))
        return redirect('service_list')

    return render(
        request,
        'services/confirm_delete.html',
        {'object': service, 'object_type': _('paslauga'), 'cancel_url': 'service_list'},
    )
