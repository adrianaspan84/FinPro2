from django import template

register = template.Library()

@register.simple_tag
def role_badge(role):
    colors = {
        'client': 'success',
        'manager': 'primary',
        'admin': 'danger',
    }
    labels = {
        'client': 'Klientas',
        'manager': 'Vadibininkas',
        'admin': 'Administratorius',
    }

    color = colors.get(role, 'secondary')
    label = labels.get(role, role)

    return f'<span class="badge bg-{color}">{label}</span>'
