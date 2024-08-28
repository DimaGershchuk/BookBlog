from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Genre, Author, Book, Comments
from .forms import CommentsForm, EditRatingForm, BookForm


def book_list(request):

    books = Book.objects.annotate(avg_rating=Avg('reviews__rating'))

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

    return render(request, 'books/book_list.html', {'page_obj': page_obj, 'books': page_obj.object_list})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all()
    if request.method == 'POST':
        form = CommentsForm(request.POST)
        if form.is_valid():
            reviews = form.save(commit=False)
            reviews.book = book
            reviews.author = request.user
            reviews.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = CommentsForm()

    return render(request, 'books/book_detail.html', {'book': book, 'reviews': reviews, 'form': form})


def edit_rating(request, pk):
    comment = get_object_or_404(Comments, pk=pk)
    if comment.author != request.user:
        return HttpResponseForbidden("Ви не маєте дозволу редагувати цей коментар.")
    if request.method == 'POST':
        form = EditRatingForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=comment.book.pk)
    else:
        form = EditRatingForm(instance=comment)
    return render(request, 'books/edit_rating.html', {'form': form})


def create_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})


def update_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})







