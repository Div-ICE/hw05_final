from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        views.LogOutForm.as_view(
            template_name='users/logged_out.html'
        ),
        name='logout'
    ),
    path(
        'signup/',
        views.SignUpForm.as_view(
            template_name='users/signup.html'
        ),
        name='signup'
    ),
    path(
        'password_reset_form/',
        views.PasswordResetForm.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset_form'
    ),
    path(
        'login/',
        views.LogInForm.as_view(
            template_name='users/login.html'
        ),
        name='login'
    ),
]
