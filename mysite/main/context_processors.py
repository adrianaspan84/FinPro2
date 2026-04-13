from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

import json


VISIT_COUNTER_PATH = 'settings/visit_counter.json'


def _next_global_visit_counter():
    total_visits = 0

    if default_storage.exists(VISIT_COUNTER_PATH):
        try:
            with default_storage.open(VISIT_COUNTER_PATH, 'r') as counter_file:
                data = json.load(counter_file)
            total_visits = int(data.get('total_visits', 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            total_visits = 0

    total_visits += 1

    payload = {'total_visits': total_visits}
    if default_storage.exists(VISIT_COUNTER_PATH):
        default_storage.delete(VISIT_COUNTER_PATH)
    default_storage.save(VISIT_COUNTER_PATH, ContentFile(json.dumps(payload)))

    return total_visits


def company_info(request):
    visit_counter = _next_global_visit_counter()

    return {
        'company_info': settings.COMPANY_INFO,
        'visit_counter': visit_counter,
    }

