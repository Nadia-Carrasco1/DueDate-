# Interfaz/context_processors.py
from .models import CalendarioPage, CronometroPage
from Usuarios.models import RegistroPage

def global_pages(request):
    return {
        "calendario_page": CalendarioPage.objects.live().first(),
        "cronometro_page": CronometroPage.objects.live().first(),
        "registro_page": RegistroPage.objects.live().first(),

    }
