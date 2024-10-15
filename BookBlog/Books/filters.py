from django_filters import rest_framework as filters
from .models import Book
from rest_framework import generics
from django_filters import rest_framework as filters
from .serializers import BookSerializer


# Клас для фільтрації
class BookFilter(filters.FilterSet):
    genre = filters.CharFilter(field_name='genre__name', lookup_expr='icontains')
    author = filters.CharFilter(field_name='author__name', lookup_expr='icontains')
    publication_date = filters.DateFromToRangeFilter(field_name='publication_date')


    class Meta:
        model = Book
        fields = ['genre', 'author', 'publication_date']
