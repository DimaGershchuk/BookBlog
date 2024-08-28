from django import forms
from django.core.exceptions import ValidationError
from .models import Comments, Book, Author, Genre


class CommentsForm(forms.ModelForm):
    rating = forms.IntegerField(label='Оцінка', widget=forms.NumberInput(attrs={'class': 'form-input'}))
    comment = forms.CharField(label='Коментар', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Comments
        fields = ['rating', 'comment']


class EditRatingForm(forms.ModelForm):
    rating = forms.IntegerField(label='Новий рейтинг', widget=forms.NumberInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Comments
        fields = ['rating']


class BookForm(forms.ModelForm):
    title = forms.CharField(label='Назва книги', widget=forms.TextInput(attrs={'class': 'form-input'}))
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        label='Оберіть автора',
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=False
    )
    new_author = forms.CharField(
        label='Або введіть нового автора',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        label='Оберіть жанр',
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=False
    )
    new_genre = forms.CharField(
        label='Або введіть новий жанр',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )

    description = forms.CharField(label='Опис книги', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Book
        fields = ['title', 'author', 'new_author', 'genre', 'new_genre', 'description']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        author = cleaned_data.get("author")
        new_author = cleaned_data.get("new_author")
        genre = cleaned_data.get("genre")
        new_genre = cleaned_data.get("new_genre")

        # Перевірка на обрання або створення нового автора
        if not author and not new_author:
            raise ValidationError("Будь ласка, оберіть автора або введіть нового автора.")

        # Вибір автора: існуючого або нового
        selected_author = author
        if new_author:
            selected_author, created = Author.objects.get_or_create(name=new_author)

        # Перевірка на дублювання книги з обраним або новим автором
        if Book.objects.filter(title=title, author=selected_author).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Книга з такою назвою і автором вже існує в каталозі.")

        # Перевірка на обрання або створення нового жанру
        if not genre and not new_genre:
            raise ValidationError("Будь ласка, оберіть жанр або введіть новий жанр.")

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
