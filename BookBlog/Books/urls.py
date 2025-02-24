from django.urls import path, include
from .views import book_list, book_detail, edit_rating, create_book, update_book, BookByGenreView, BookListCreateView, BookDetailView, AuthorListCreateView, AuthorDetailView, GenreListCreateView, GenreDetailView, CommentListCreateView, CommentDetailView, RatingListCreateView, RatingDetailView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('', book_list, name='book_list'),
    path('detail/<int:pk>/', book_detail, name='book_detail'),
    path('edit_rating/<int:pk>/', edit_rating, name='edit_rating'),
    path('create/', create_book, name='create_book'),
    path('update/<int:pk>/', update_book, name='update_book'),

    path('api/books/genre/<int:genre_id>/', BookByGenreView.as_view(), name='book-by-genre'),

    path('api/books/', BookListCreateView.as_view(), name='book-list-create'),
    path('api/books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('api/authors/', AuthorListCreateView.as_view(), name='author-list-create'),
    path('api/authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('api/genres/', GenreListCreateView.as_view(), name='genre-list-create'),
    path('api/genres/<int:pk>/', GenreDetailView.as_view(), name='genre-detail'),
    path('api/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('api/comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('api/ratings/', RatingListCreateView.as_view(), name='rating-list-create'),
    path('api/ratings/<int:pk>/', RatingDetailView.as_view(), name='rating-detail')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

