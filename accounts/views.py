from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import ProfileForm, RegistrationForm
from .models import User


def home(request):
    return redirect("dashboard" if request.user.is_authenticated else "login")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user, backend="accounts.backends.EmailOrUsernameBackend")
            messages.success(request, f"Welcome to CraftLoom, {user.first_name}! Your account was created.")
            return redirect("dashboard")
        messages.error(request, "Registration failed. Please fix the errors below.")
    return render(request, "accounts/register.html", {"form": form})


class CraftLoomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().display_name}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username/email or password.")
        return super().form_invalid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


@login_required
def dashboard(request):
    return redirect("admin_dashboard" if request.user.is_admin_role else "artisan_dashboard")


@role_required(User.Role.ARTISAN)
def artisan_dashboard(request):
    modules = [
        ("Supply Manager", "Track raw materials, categories and units.", "supplies:list"),
        ("Recipe & Pricing Creator", "Build product recipes and see exact unit costs.", None),
        ("Production Logger", "Log batches and auto-deduct stock.", None),
    ]
    return render(request, "accounts/dashboard_artisan.html", {"modules": modules})


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    context = {
        "total_users": User.objects.count(),
        "artisan_count": User.objects.filter(role=User.Role.ARTISAN).count(),
        "admin_count": User.objects.filter(role=User.Role.ADMIN).count(),
        "users": User.objects.order_by("-date_joined")[:25],
    }
    return render(request, "accounts/dashboard_admin.html", context)


@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"profile_user": request.user})


@login_required
def profile_edit(request):
    # Only ever edits request.user, so nobody can touch another profile.
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated.")
            return redirect("profile")
        messages.error(request, "Could not update profile. Please fix the errors below.")
    return render(request, "accounts/profile_edit.html", {"form": form})
