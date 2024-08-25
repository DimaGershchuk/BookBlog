from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Genre, Author, Book, Comments
from .forms import CommentsForm, EditRatingForm, BookForm


def book_list(request):

    books = Book.objects.all()

    genre = request.GET.get('genre')
    author = request.GET.get('author')
    rating = request.GET.get('rating')

    if genre:
        books = books.filter(genre__name=genre)
    if author:
        books = books.filter(author__name=author)
    if rating:
        books = books.filter(rating__gte=rating)

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
            reviews.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = CommentsForm()

    return render(request, 'books/book_detail.html', {'book': book, 'reviews': reviews, 'form': form})


def edit_rating(request, pk):
    comment = get_object_or_404(Comments, pk=pk)
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
            form.save()
            return redirect('book_detail')
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







