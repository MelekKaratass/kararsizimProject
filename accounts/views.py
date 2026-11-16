from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import EmailLoginForm, RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("polls:home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        request.session["registration_completed"] = True
        return redirect("accounts:registration_success")
    return render(request, "accounts/register.html", {"form": form})


def registration_success(request):
    if not request.session.pop("registration_completed", False):
        return redirect("accounts:register")
    return render(request, "accounts/registration_success.html")


class EmailLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Oturumun kapatıldı.")
    return redirect("polls:home")
