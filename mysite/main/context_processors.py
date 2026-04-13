from django.conf import settings


def company_info(request):
    return {
        'company_info': settings.COMPANY_INFO,
    }

