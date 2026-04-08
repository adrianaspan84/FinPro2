from django import template

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
        'new': 'Naujas',
        'in_progress': 'Vykdomas',
        'done': 'Atliktas',
        'cancelled': 'Atšauktas',
    }

    color = colors.get(status, 'secondary')
    label = labels.get(status, status)

    return f'<span class="badge bg-{color}">{label}</span>'
