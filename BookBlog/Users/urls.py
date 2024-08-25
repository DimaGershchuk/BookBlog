from django.urls import path
from .views import home_view, RegisterUser, LoginUser, logout_user
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('', home_view, name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
]

