from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Genre, Author, Book, Comments, Rating
from .forms import CommentsForm, EditRatingForm, BookForm, RatingForm


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
    reviews = book.reviews.all()

    user_rating = Rating.objects.filter(user=request.user, book=book).first() if request.user.is_authenticated else None

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

    return render(request, 'books/book_detail.html', {'book': book, 'reviews': reviews, 'comments_form': comments_form, 'rating_form': rating_form, 'user_rating': user_rating})


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







