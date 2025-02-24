from django import forms
from django.core.exceptions import ValidationError
from .models import Comments, Book, Author, Genre, Rating


class CommentsForm(forms.ModelForm):
    comment = forms.CharField(label='Comment', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Comments
        fields = ['comment']


class EditRatingForm(forms.ModelForm):
    rating = forms.IntegerField(label='New rate', widget=forms.NumberInput(attrs={'class': 'form-input'}), min_value=1, max_value=10)

    class Meta:
        model = Comments
        fields = ['rating']


class RatingForm(forms.ModelForm):
    rating = forms.IntegerField(
        label='Rate',
        widget=forms.NumberInput(attrs={'class': 'form-input'}),
        min_value=1,
        max_value=10
    )

    class Meta:
        model = Rating
        fields = ['rating']


class BookForm(forms.ModelForm):
    title = forms.CharField(label='Book name', widget=forms.TextInput(attrs={'class': 'form-input'}))
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        label='Select author',
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=False
    )
    new_author = forms.CharField(
        label='Or put new author',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        label='Select genre',
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=False
    )
    new_genre = forms.CharField(
        label='Or put new genre',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )

    description = forms.CharField(label='Boo description', widget=forms.TextInput(attrs={'class': 'form-input'}))

    image = forms.ImageField()

    class Meta:
        model = Book
        fields = ['title', 'author', 'new_author', 'genre', 'new_genre', 'description', 'image']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        author = cleaned_data.get("author")
        new_author = cleaned_data.get("new_author")
        genre = cleaned_data.get("genre")
        new_genre = cleaned_data.get("new_genre")

        # Перевірка на обрання або створення нового автора
        if not author and not new_author:
            raise ValidationError("Please select or create new author")

        # Вибір автора: існуючого або нового
        selected_author = author
        if new_author:
            selected_author, created = Author.objects.get_or_create(name=new_author)

        # Перевірка на дублювання книги з обраним або новим автором
        if Book.objects.filter(title=title, author=selected_author).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Book whith this name and author already exists")

        # Перевірка на обрання або створення нового жанру
        if not genre and not new_genre:
            raise ValidationError("Please select or create new genre")

        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        new_author_name = cleaned_data.get('new_author')
        new_genre_name = cleaned_data.get('new_genre')

        # Створення нового автора, якщо введено і ще не існує
        if new_author_name:
            self.instance.author, created = Author.objects.get_or_create(name=new_author_name)

        # Створення нового жанру, якщо введено і ще не існує
        if new_genre_name:
            self.instance.genre, created = Genre.objects.get_or_create(name=new_genre_name)

        return super().save(commit=commit)
