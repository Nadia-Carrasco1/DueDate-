from django.shortcuts import redirect
from allauth.account.views import SignupView, EmailVerificationSentView, ConfirmEmailView
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.socialaccount.models import SocialAccount

class MySignupView(SignupView):
    template_name = "registro_page.html"

    def form_valid(self, form):
            user = form.save(self.request)

            if not SocialAccount.objects.filter(user=user).exists():
                user.is_active = False
                user.save()

                email_address, created = EmailAddress.objects.get_or_create(
                    user=user,
                    email=user.email,
                    defaults={'verified': False, 'primary': True}
                )

                email_address.send_confirmation(self.request, signup=True)

                self.request.session["signup_email"] = user.email
                return redirect("account_email_verification_sent")

            else:
                user.is_active = True
                user.save()
                return redirect("/") 
    
class MyEmailVerificationSentView(EmailVerificationSentView):
    template_name = "account/email_verification_sent.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.request.session.get("signup_email", "")
        return context


class MyConfirmEmailView(ConfirmEmailView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = super().get(request, *args, **kwargs)

        email_address = self.object.email_address
        if email_address and email_address.verified:
            user = email_address.user
            if not user.is_active:
                user.is_active = True
                user.save()

        return redirect("account_login")