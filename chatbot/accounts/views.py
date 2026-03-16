from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class LoginView(auth_views.LoginView):
    template_name = "registration/login.html"
    next_page = reverse_lazy("chat:new_chat")


class LogoutView(auth_views.LogoutView):
    template_name = "registration/logged_out.html"
    next_page = "/"


class PasswordResetView(auth_views.PasswordResetView):
    template_name = "registration/password_reset_form.html"


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
