from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUpForm(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordResetForm(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('templates/users/password_reset_confirm.html')
    template_name = 'users/password_reset_form.html'


class LogOutForm(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/logged_out_form.html'


class LogInForm(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/login.html'


class PasswordChangeForm(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('templates/users/password_change_done.html')
    template_name = 'users/password_change_form.html'
