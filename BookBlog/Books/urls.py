from django.urls import path
from .views import book_list, book_detail, edit_rating, create_book, update_book
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('', book_list, name='book_list'),
    path('detail/<int:pk>/', book_detail, name='book_detail'),
    path('edit_rating/<int:pk>/', edit_rating, name='edit_rating'),
    path('create/', create_book, name='create_book'),
    path('update/<int:pk>/', update_book, name='update_book')

]

