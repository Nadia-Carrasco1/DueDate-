from allauth.account.views import ConfirmEmailView as AllauthConfirmEmailView

class MyConfirmEmailView(AllauthConfirmEmailView):
    template_name = "account/confirm_email.html"
