from django.urls import path, include
from .views import book_list, book_detail, edit_rating, create_book, update_book, BookByGenreView
from django.contrib.auth.views import LoginView
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, AuthorViewSet, BookViewSet, CommentViewSet, RatingViewSet


router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('', book_list, name='book_list'),
    path('detail/<int:pk>/', book_detail, name='book_detail'),
    path('edit_rating/<int:pk>/', edit_rating, name='edit_rating'),
    path('create/', create_book, name='create_book'),
    path('update/<int:pk>/', update_book, name='update_book'),
    path('api/books/genre/<int:genre_id>/', BookByGenreView.as_view(), name='book-by-genre'),  # Новий маршрут
    path('api/', include(router.urls)),

]

