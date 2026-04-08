from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.conf import settings
from .forms import OrderCreateForm
from .models import OrderItem
from orders.utils.pdf import generate_invoice_pdf

from services.models import Service
from .forms import OrderEditForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Order


@login_required
def order_change_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id)

    if request.user.profile.role not in ["manager", "admin"]:
        return HttpResponseForbidden("Neturi teisės keisti statuso")

    order.status = new_status
    order.manager = request.user
    order.save()

    return redirect("order_detail", order_id)




@login_required
def client_dashboard(request):
    if request.user.profile.role != 'client':
        raise PermissionDenied("Šis puslapis skirtas tik klientams.")

    user = request.user

    active_orders = Order.objects.filter(client=user, status='in_progress')
    new_orders = Order.objects.filter(client=user, status='new')
    done_orders = Order.objects.filter(client=user, status='done')
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
    # Tik vadibininkai ir adminai gali matyti šį puslapį
    if request.user.profile.role not in ['manager', 'admin']:
        raise PermissionDenied("Neturite teisės pasiekti šio puslapio.")

    user = request.user

    # Admin mato viską, vadibininkas – tik savo
    if user.profile.role == 'admin':
        active_orders = Order.objects.filter(status='in_progress')
        new_orders = Order.objects.filter(status='new')
        done_orders = Order.objects.filter(status='done')
        overdue_orders = [o for o in active_orders if o.is_overdue]
    else:
        active_orders = Order.objects.filter(manager=user, status='in_progress')
        new_orders = Order.objects.filter(manager=user, status='new')
        done_orders = Order.objects.filter(manager=user, status='done')
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
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Leidimai
    if request.user.profile.role == 'client':
        raise PermissionDenied("Klientai negali redaguoti užsakymų.")

    # Vadibininkas gali redaguoti tik jam priskirtus užsakymus
    if request.user.profile.role == 'manager' and order.manager != request.user:
        raise PermissionDenied("Negalite redaguoti šio užsakymo.")

    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)

        # Vadibininkui paslepiame manager lauką
        if request.user.profile.role == 'manager':
            form.fields.pop('manager')

        if form.is_valid():
            form.save()
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderEditForm(instance=order)

        # Vadibininkui paslepiame manager lauką
        if request.user.profile.role == 'manager':
            form.fields.pop('manager')

    return render(request, 'orders/order_edit.html', {'form': form, 'order': order})


@login_required
def order_list(request):
    user = request.user

    # Admin mato viską
    if user.is_superuser or user.profile.role == 'admin':
        orders = Order.objects.all()

    # Vadibininkas mato tik jam priskirtus
    elif user.profile.role == 'manager':
        orders = Order.objects.filter(manager=user)

    # Klientas mato tik savo užsakymus
    else:
        orders = Order.objects.filter(client=user)

    # Filtravimas pagal statusą
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    return render(request, 'orders/order_list.html', {
        'orders': orders,
        'selected_status': status,
    })


@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = request.user
            order.save()

            # Sukuriame eilutę
            OrderItem.objects.create(
                order=order,
                service=form.cleaned_data['service'],
                quantity=form.cleaned_data['quantity']
            )

            # Automatinis vadibininko priskyrimas
            order.assign_manager()

            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_form.html', {'form': form})


def load_services(request):
    category_id = request.GET.get('category_id')
    services = Service.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(services), safe=False)


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})


def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Sugeneruojame PDF
    pdf_path = generate_invoice_pdf(order)

    # Priskiriame PDF failą užsakymui, jei dar nėra
    if not order.pdf_file:
        order.pdf_file = pdf_path
        order.save()

    full_path = f"{settings.MEDIA_ROOT}/{pdf_path}"

    return FileResponse(open(full_path, 'rb'), content_type='application/pdf')
