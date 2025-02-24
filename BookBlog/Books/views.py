from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit
from rest_framework import viewsets, permissions, generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Genre, Author, Book, Comments, Rating
from .forms import CommentsForm, EditRatingForm, BookForm, RatingForm
from .serializers import GenreSerializer, AuthorSerializer, BookSerializer, CommentSerializer, RatingSerializer
from .pagination import MyPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BookFilter


@ratelimit(key='ip', rate='10/m', block=True)
def book_list(request):
    genre_param = request.GET.get('genre', '')
    author_param = request.GET.get('author', '')
    min_rating = request.GET.get('min_rating', '')
    max_rating = request.GET.get('max_rating', '')

    cache_key = f"book_list_{genre_param}_{author_param}_{min_rating}_{max_rating}"
    books = cache.get(cache_key)

    if books is None:
        books = Book.objects.select_related('author', 'genre').all()
        if genre_param:
            books = books.filter(genre__name__icontains=genre_param)
        if author_param:
            books = books.filter(author__name__icontains=author_param)
        if min_rating:
            books = books.filter(average_rating__gte=min_rating)
        if max_rating:
            books = books.filter(average_rating__lte=max_rating)
        books = list(books)
        cache.set(cache_key, books, timeout=900)

    authors = Author.objects.all()
    genres = Genre.objects.all()

    paginator = Paginator(books, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'books/book_list.html', {
        'page_obj': page_obj,
        'books': page_obj.object_list,
        'authors': authors,
        'genres': genres
    })


@cache_page(60 * 15)
def book_detail(request, pk):

    book = get_object_or_404(Book.objects.select_related('author', 'genre'), pk=pk)

    reviews = book.reviews.select_related('author').all()  # Отримання всіх відгуків з автором

    ratings = Rating.objects.filter(book=book).select_related('user')
    rating_dict = {rating.user.id: rating for rating in ratings}

    reviews_with_ratings = [
        {
            'review': review,
            'rating': rating_dict.get(review.author.id)
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

    return render(request, 'books/book_detail.html', {'book': book,  'reviews_with_ratings': reviews_with_ratings, 'reviews': reviews, 'comments_form': comments_form, 'rating_form': rating_form, 'user_rating': ratings})


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
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
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
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})


@method_decorator(ratelimit(key='ip', rate='10/m', block=True), name='dispatch')
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter
    pagination_class = MyPageNumberPagination
    parser_classes = (MultiPartParser, FormParser, JSONParser)


@method_decorator(ratelimit(key='ip', rate='10/m', block=True), name='dispatch')
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




