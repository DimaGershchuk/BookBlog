from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions, generics
from .models import Genre, Author, Book, Comments, Rating
from .forms import CommentsForm, EditRatingForm, BookForm, RatingForm
from .serializers import GenreSerializer, AuthorSerializer, BookSerializer, CommentSerializer, RatingSerializer
from .pagination import MyPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BookFilter


def book_list(request):

    books = Book.objects.all()

    authors = Author.objects.all()
    genres = Genre.objects.all()

    genre = request.GET.get('genre')
    author = request.GET.get('author')
    min_rating = request.GET.get('min_rating')
    max_rating = request.GET.get('max_rating')

    if genre:
        books = books.filter(genre__name__icontains=genre)
    if author:
        books = books.filter(author__name__icontains=author)
    if min_rating:
        books = books.filter(avg_rating__gte=min_rating)
    if max_rating:
        books = books.filter(avg_rating__lte=max_rating)

    paginator = Paginator(books, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'books/book_list.html', {'page_obj': page_obj, 'books': page_obj.object_list, 'authors': authors, 'genres': genres})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.select_related('author').all()  # Отримання всіх відгуків з автором

    user_rating = Rating.objects.filter(user=request.user, book=book).first() if request.user.is_authenticated else None

    reviews_with_ratings = [
        {
            'review': review,
            'rating': Rating.objects.filter(user=review.author, book=book).first()
        }
        for review in reviews
    ]

    if request.method == 'POST':
        comments_form = CommentsForm(request.POST)
        if comments_form.is_valid():
            comment = comments_form.save(commit=False)
            comment.book = book
            comment.author = request.user
            comment.save()
            book.calculate_rating()
            return redirect('book_detail', pk=book.pk)

        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.user = request.user
            rating.book = book
            rating.save()
            book.calculate_rating()
            return redirect('book_detail', pk=book.pk)

    else:
        comments_form = CommentsForm()
        rating_form = RatingForm()

    return render(request, 'books/book_detail.html', {'book': book,  'reviews_with_ratings': reviews_with_ratings, 'reviews': reviews, 'comments_form': comments_form, 'rating_form': rating_form, 'user_rating': user_rating})


def edit_rating(request, pk):
    rating = get_object_or_404(Rating, pk=pk)
    if rating.user != request.user:
        return HttpResponseForbidden("Ви не маєте дозволу редагувати цю оцінку.")
    if request.method == 'POST':
        form = EditRatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            rating.book.calculate_rating()
            return redirect('book_detail', pk=rating.book.pk)
    else:
        form = EditRatingForm(instance=rating)
    return render(request, 'books/edit_rating.html', {'form': form})


def create_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user  # Зберігаємо автора публікації
            book.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})


def update_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.user != book.created_by and not request.user.is_staff:
        return HttpResponseForbidden("Ви не маєте дозволу редагувати цю книгу.")

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter
    pagination_class = MyPageNumberPagination


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]


class GenreListCreateView(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticated]


class GenreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


class RatingListCreateView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]


class RatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BookByGenreView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        genre_id = self.kwargs['genre_id']
        return Book.objects.filter(genre_id=genre_id)




