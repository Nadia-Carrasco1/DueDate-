from django.conf import settings
from wagtail.models import Page
from allauth.account.forms import SignupForm
from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings
from django.template.response import TemplateResponse
from django.shortcuts import redirect  


class RegistroPage(Page):
    template = "registro_page.html"

    def get_context(self, request):
        context = super().get_context(request)
        context["form"] = SignupForm()
        return context

    def serve(self, request):
        if request.user.is_authenticated:
            return redirect('/')  

        form = SignupForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                try:
                    user = form.save(request)
                except ValueError:
                    form.add_error('email', "Ya existe un usuario registrado con este correo electrónico.")
                else:
                    return complete_signup(
                        request,
                        user,
                        allauth_settings.EMAIL_VERIFICATION,
                        settings.LOGIN_REDIRECT_URL,
                    )

        context = self.get_context(request)
        context["form"] = form
        return TemplateResponse(request, self.get_template(request), context)
