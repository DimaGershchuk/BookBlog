from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import home_view, RegisterUser, LoginUser, logout_user, CustomUserListCreateView, CustomUserDetailView
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('', home_view, name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('api/users/', CustomUserListCreateView.as_view(), name='create-user'),
    path('api/users/<int:pk>/', CustomUserDetailView.as_view(), name='detail-user')
]

 