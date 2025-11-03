from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.blocks import StructBlock, CharBlock, RichTextBlock, URLBlock
from wagtail.admin.panels import FieldPanel
from datetime import timedelta 
from wagtail.snippets.models import register_snippet
from django.utils import timezone


class SectionBlock(StructBlock):
    heading = CharBlock(required=True, help_text="Título de la sección")
    content = RichTextBlock(required=True, help_text="Contenido de la sección")

    class Meta:
        icon = "placeholder"
        label = "Sección"

class DashboardBlock(StructBlock):
    title = CharBlock(required=True, help_text="Título de la sección")
    content = RichTextBlock(required=True, help_text="Contenido de la sección")
    link = URLBlock(required=False, help_text="Enlace opcional")

    class Meta:
        icon = "placeholder"
        label = "Bloque de dashboard"


class HomePage(Page):
    template = "home_page.html"

    intro_title = models.CharField(max_length=255, blank=True)
    body = RichTextField(blank=True)

    sections = StreamField([
        ('section', SectionBlock()),
    ], blank=True, use_json_field=True)

    dashboard_blocks = StreamField([
        ('block', DashboardBlock()),
    ], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro_title'),
        FieldPanel('body'),
        FieldPanel('sections'),
        FieldPanel('dashboard_blocks'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        if request.user.is_authenticated:
            context["tasks"] = Task.objects.order_by("completed", "due_date")[:9]
        else:
            context["tasks"] = []  
        return context


class CalendarioPage(Page):
    template = "calendario_page.html"

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        if request.user.is_authenticated:
            context["tasks"] = Task.objects.exclude(due_date__isnull=True)
        else:
            context["tasks"] = []
        return context


# -Tareas
@register_snippet
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    reminder = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def status(self):
        if self.completed:
            return "completada"
        if self.due_date:
            now = timezone.now()
            if self.due_date < now:
                return "vencida" 
        return "pendiente"
    
# -Cronómetro
class CronometroPage(Page):
    template = "cronometro_page.html" 

    tiempo_estudio = models.DurationField(
        null=True,
        blank=True,
        default=timedelta(minutes=50),
        help_text="Tiempo de estudio"
    )

    tiempo_descanso = models.DurationField(
        null=True,
        blank=True,
        default=timedelta(minutes=10),
        help_text="Tiempo de descanso"
    )

    content_panels = Page.content_panels + [
        FieldPanel('tiempo_estudio'),
        FieldPanel('tiempo_descanso')
    ]