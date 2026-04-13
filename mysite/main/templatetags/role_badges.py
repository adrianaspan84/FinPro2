from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from main.models import Profile

register = template.Library()


@register.simple_tag
def get_or_create_profile(user):
    if not user or not getattr(user, 'is_authenticated', False):
        return None
    profile, _ = Profile.objects.get_or_create(user=user)
    # Superuser → admin, staff (non-superuser) → staff, others keep their role.
    if user.is_superuser:
        if profile.role != 'admin':
            profile.role = 'admin'
            profile.save(update_fields=['role'])
    elif user.is_staff:
        if profile.role != 'staff':
            profile.role = 'staff'
            profile.save(update_fields=['role'])
    return profile


@register.simple_tag
def role_badge(role):
    colors = {
        'client': 'success',
        'manager': 'primary',
        'admin': 'danger',
        'staff': 'warning',
    }
    labels = {
        'client': _('Klientas'),
        'manager': _('Vadybininkas'),
        'admin': _('Administratorius'),
        'staff': _('Darbuotojas'),
    }

    color = colors.get(role, 'secondary')
    label = labels.get(role, role)

    return mark_safe(f'<span class="badge bg-{color}">{label}</span>')
