from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout

from .forms import CustomUserCreationForm, LoginUserForm
from django.shortcuts import render, redirect
from django.views.generic import CreateView


def home_view(request):
    return render(request, 'home_page.html')


class RegisterUser(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'

    def get_success_url(self):
        return reverse_lazy('home')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')




