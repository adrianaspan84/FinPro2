import json
from urllib.parse import urlencode
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from orders.utils.pdf import generate_invoice_pdf
from services.models import Service, ServiceCategory

from .forms import OrderCreateForm, OrderEditForm
from .models import Order, OrderItem


def _apply_order_filters(queryset, status=None, q=''):
    if status:
        queryset = queryset.filter(status=status)

    q = (q or '').strip()
    if q:
        query_filter = Q(client__username__icontains=q)
        if q.isdigit():
            query_filter |= Q(id=int(q))
        queryset = queryset.filter(query_filter)

    return queryset


@login_required
def order_change_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id, is_deleted=False)

    if request.user.profile.role not in ["manager", "admin"]:
        return HttpResponseForbidden(_("Neturi teisės keisti statuso"))

    order.status = new_status
    order.manager = request.user
    order.save()

    return redirect("order_detail", order_id)


@login_required
def client_dashboard(request):
    if request.user.profile.role != 'client':
        raise PermissionDenied(_("Šis puslapis skirtas tik klientams."))

    user = request.user

    active_orders = Order.objects.filter(client=user, status='in_progress', is_deleted=False)
    new_orders = Order.objects.filter(client=user, status='new', is_deleted=False)
    done_orders = Order.objects.filter(client=user, status='done', is_deleted=False)
    overdue_orders = [o for o in active_orders if o.is_overdue]

    context = {
        'active_orders': active_orders,
        'new_orders': new_orders,
        'done_orders': done_orders,
        'overdue_orders': overdue_orders,
        'stats': {
            'active': active_orders.count(),
            'new': new_orders.count(),
            'done': done_orders.count(),
            'overdue': len(overdue_orders),
        }
    }

    return render(request, 'orders/client_dashboard.html', context)


@login_required
def manager_dashboard(request):
    if request.user.profile.role not in ['manager', 'admin']:
        raise PermissionDenied(_("Neturite teisės pasiekti šio puslapio."))

    user = request.user

    if user.profile.role == 'admin':
        active_orders = Order.objects.filter(status='in_progress', is_deleted=False)
        new_orders = Order.objects.filter(status='new', is_deleted=False)
        done_orders = Order.objects.filter(status='done', is_deleted=False)
        overdue_orders = [o for o in active_orders if o.is_overdue]
    else:
        active_orders = Order.objects.filter(manager=user, status='in_progress', is_deleted=False)
        new_orders = Order.objects.filter(manager=user, status='new', is_deleted=False)
        done_orders = Order.objects.filter(manager=user, status='done', is_deleted=False)
        overdue_orders = [o for o in active_orders if o.is_overdue]

    context = {
        'active_orders': active_orders,
        'new_orders': new_orders,
        'done_orders': done_orders,
        'overdue_orders': overdue_orders,
        'stats': {
            'active': active_orders.count(),
            'new': new_orders.count(),
            'done': done_orders.count(),
            'overdue': len(overdue_orders),
        }
    }

    return render(request, 'orders/manager_dashboard.html', context)


@login_required
def admin_dashboard(request):
    if request.user.profile.role != 'admin':
        raise PermissionDenied(_("Neturite teisės pasiekti šio puslapio."))

    include_deleted = request.GET.get('include_deleted') == '1'
    status = request.GET.get('status')
    q = (request.GET.get('q') or '').strip()

    all_orders = _apply_order_filters(Order.objects.filter(is_deleted=False), status=status, q=q)
    active_orders = all_orders.filter(status='in_progress')
    new_orders = all_orders.filter(status='new')
    done_orders = all_orders.filter(status='done')
    overdue_orders = [o for o in active_orders if o.is_overdue]
    deleted_orders = (
        _apply_order_filters(Order.objects.filter(is_deleted=True), status=status, q=q)
        if include_deleted else Order.objects.none()
    )

    context = {
        'all_orders': all_orders,
        'active_orders': active_orders,
        'new_orders': new_orders,
        'done_orders': done_orders,
        'overdue_orders': overdue_orders,
        'deleted_orders': deleted_orders,
        'include_deleted': include_deleted,
        'selected_status': status,
        'search_query': q,
        'stats': {
            'total': all_orders.count(),
            'active': active_orders.count(),
            'new': new_orders.count(),
            'done': done_orders.count(),
            'overdue': len(overdue_orders),
            'deleted': deleted_orders.count() if include_deleted else 0,
        }
    }

    return render(request, 'orders/admin_dashboard.html', context)


@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, is_deleted=False)

    if request.user.profile.role == 'client':
        raise PermissionDenied(_("Klientai negali redaguoti užsakymų."))

    if request.user.profile.role == 'manager' and order.manager != request.user:
        raise PermissionDenied(_("Negalite redaguoti šio užsakymo."))

    categories = ServiceCategory.objects.all()
    existing_items_payload = []

    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)

        if request.user.profile.role == 'manager':
            form.fields.pop('manager', None)

        items_error = None
        items_data = []
        raw_items = request.POST.get('items_json', '').strip()

        if raw_items:
            try:
                parsed = json.loads(raw_items)
                if not isinstance(parsed, list) or not parsed:
                    items_error = _('Pridėkite bent vieną paslaugos eilutę.')
                else:
                    existing_items_payload = parsed
                    for row in parsed:
                        service_id = int(row['service_id'])
                        quantity = Decimal(str(row['quantity']))
                        price = Decimal(str(row['price']))

                        if quantity <= 0 or price <= 0:
                            items_error = _('Kiekis ir kaina turi būti didesni už 0.')
                            break

                        items_data.append({
                            'service_id': service_id,
                            'quantity': quantity,
                            'price': price,
                        })
            except (json.JSONDecodeError, KeyError, TypeError, ValueError, InvalidOperation):
                items_error = _('Neteisingas eilučių formatas.')
        else:
            items_error = _('Pridėkite bent vieną paslaugos eilutę.')

        services = {}
        if not items_error:
            service_ids = [item['service_id'] for item in items_data]
            services = Service.objects.in_bulk(service_ids)
            if len(services) != len(set(service_ids)):
                items_error = _('Pasirinkta neegzistuojanti paslauga.')

        if form.is_valid() and not items_error:
            with transaction.atomic():
                form.save()
                order.items.all().delete()
                for row in items_data:
                    OrderItem.objects.create(
                        order=order,
                        service=services[row['service_id']],
                        quantity=row['quantity'],
                        custom_price=row['price'],
                    )
            return redirect('order_detail', order_id=order.id)

        existing_items_json = raw_items or '[]'

    else:
        form = OrderEditForm(instance=order)

        if request.user.profile.role == 'manager':
            form.fields.pop('manager', None)

        existing_items = [
            {
                'service_id': item.service_id,
                'name': item.service.name,
                'price': float(item.unit_price),
                'quantity': float(item.quantity),
            }
            for item in order.items.select_related('service').all()
        ]
        existing_items_payload = existing_items
        existing_items_json = json.dumps(existing_items)
        items_error = None

    return render(request, 'orders/order_edit.html', {
        'form': form,
        'order': order,
        'existing_items_json': existing_items_json,
        'existing_items_payload': existing_items_payload,
        'categories': categories,
        'items_error': items_error,
    })


@login_required
def order_list(request):
    user = request.user

    if user.is_superuser or user.profile.role == 'admin':
        orders = Order.objects.filter(is_deleted=False)
    elif user.profile.role == 'manager':
        orders = Order.objects.filter(manager=user, is_deleted=False)
    else:
        orders = Order.objects.filter(client=user, is_deleted=False)

    status = request.GET.get('status')
    q = (request.GET.get('q') or '').strip()
    orders = _apply_order_filters(orders, status=status, q=q)

    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    params = {}
    if status:
        params['status'] = status
    if q:
        params['q'] = q
    query_suffix = f"&{urlencode(params)}" if params else ''

    return render(request, 'orders/order_list.html', {
        'orders': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.paginator.num_pages > 1,
        'query_suffix': query_suffix,
        'selected_status': status,
        'search_query': q,
    })


@login_required
@require_POST
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, is_deleted=False)

    if request.user.profile.role == 'client':
        raise PermissionDenied(_("Klientai negali trinti užsakymų."))

    if request.user.profile.role == 'manager' and order.manager != request.user:
        raise PermissionDenied(_("Negalite trinti šio užsakymo."))

    order.soft_delete()
    next_url = request.POST.get('next', '')
    if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
        return redirect(next_url)
    return redirect('order_list')


@login_required
@require_POST
def restore_order(request, order_id):
    if request.user.profile.role != 'admin':
        raise PermissionDenied(_("Tik administratorius gali atkurti užsakymus."))

    order = get_object_or_404(Order, id=order_id, is_deleted=True)
    order.is_deleted = False
    order.deleted_at = None
    order.save(update_fields=['is_deleted', 'deleted_at'])
    return redirect('admin_dashboard')


@login_required
def create_order(request):
    if request.user.profile.role != 'client':
        raise PermissionDenied(_("Užsakymą kurti gali tik klientas."))

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            items_data = form.cleaned_data['items_json']
            service_ids = [item['service_id'] for item in items_data]
            services = Service.objects.in_bulk(service_ids)

            if len(services) != len(set(service_ids)):
                form.add_error(None, _("Pasirinkta neegzistuojanti paslauga."))
            else:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.client = request.user
                    order.save()

                    for row in items_data:
                        OrderItem.objects.create(
                            order=order,
                            service=services[row['service_id']],
                            quantity=row['quantity'],
                        )

                    order.assign_manager()

                return redirect('order_list')
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_form.html', {'form': form})


@login_required
def load_services(request):
    category_id = request.GET.get('category_id')
    services = Service.objects.filter(category_id=category_id).values('id', 'name', 'price', 'unit')
    data = [
        {
            'id': s['id'],
            'name': s['name'],
            'price': float(s['price']),
            'unit': s['unit'],
        }
        for s in services
    ]
    return JsonResponse(data, safe=False)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, is_deleted=False)

    if request.user.profile.role == 'client' and order.client != request.user:
        raise PermissionDenied(_("Negalite peržiūrėti šio užsakymo."))

    if request.user.profile.role == 'manager' and order.manager != request.user:
        raise PermissionDenied(_("Negalite peržiūrėti šio užsakymo."))

    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, is_deleted=False)

    if request.user.profile.role == 'client' and order.client != request.user:
        raise PermissionDenied(_("Negalite atsisiųsti šios sąskaitos."))

    if request.user.profile.role == 'manager' and order.manager != request.user:
        raise PermissionDenied(_("Negalite atsisiųsti šios sąskaitos."))

    pdf_path = generate_invoice_pdf(order)

    if not order.pdf_file:
        order.pdf_file = pdf_path
        order.save()

    full_path = f"{settings.MEDIA_ROOT}/{pdf_path}"

    return FileResponse(open(full_path, 'rb'), content_type='application/pdf')
