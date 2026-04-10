from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

register = template.Library()

@register.simple_tag
def status_badge(status):
    colors = {
        'new': 'info',
        'in_progress': 'warning',
        'done': 'success',
        'cancelled': 'danger',
    }

    labels = {
        'new': _('Naujas'),
        'in_progress': _('Vykdomas'),
        'done': _('Atliktas'),
        'cancelled': _('Atšauktas'),
    }

    color = colors.get(status, 'secondary')
    label = labels.get(status, status)

    return mark_safe(f'<span class="badge bg-{color}">{label}</span>')
