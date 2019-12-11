from allauth.account import app_settings
from allauth.account.utils import send_email_confirmation
from allauth.account.views import SignupView
from allauth.exceptions import ImmediateHttpResponse
from django.db.models.signals import post_save
from django.shortcuts import redirect, render
from django.contrib import messages


def home(request):
    return render(request, 'core/home.html')


class CustomSignupView(SignupView):
    def form_valid(self, form):
        self.user = form.save(self.request)
        send_email_confirmation(self.request, self.user, signup=True)
        messages.info(self.request, 'that is great account')
        return redirect('account_login')
