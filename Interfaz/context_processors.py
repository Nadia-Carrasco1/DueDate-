# Interfaz/context_processors.py
from .models import CalendarioPage

def global_pages(request):
    return {
        "calendario_page": CalendarioPage.objects.live().first()
    }
