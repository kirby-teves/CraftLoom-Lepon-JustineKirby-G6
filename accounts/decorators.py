from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def role_required(role):

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if request.user.role != role:
                messages.error(request, "You don't have permission to open that page.")
                return redirect("admin_dashboard" if request.user.is_admin_role else "artisan_dashboard")
            return view(request, *args, **kwargs)

        return wrapper

    return decorator
