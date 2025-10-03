# Interfaz/context_processors.py
from .models import CalendarioPage, CronometroPage

def global_pages(request):
    return {
        "calendario_page": CalendarioPage.objects.live().first(),
        "cronometro_page": CronometroPage.objects.live().first(),
    }
