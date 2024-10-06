from django_filters import rest_framework as filters
from .models import Book
from rest_framework import generics
from django_filters import rest_framework as filters
from .serializers import BookSerializer


# Клас для фільтрації
class BookFilter(filters.FilterSet):
    genre = filters.NumberFilter(field_name='genre__id')  # Фільтр за жанром
    author = filters.NumberFilter(field_name='author__id')  # Фільтр за автором  # Фільтр за користувачем, який додав

    class Meta:
        model = Book
        fields = ['genre', 'author']
