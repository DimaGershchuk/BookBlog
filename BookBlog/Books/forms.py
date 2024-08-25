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
    title = forms.CharField(label='Назва книги ', widget=forms.TextInput(attrs={'class': 'form-input'}))
    rating = forms.IntegerField(label='Рейтинг', widget=forms.NumberInput(attrs={'class': 'form-input'}))

    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        label='Оберіть автора',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        label='Оберіть жанр',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Book
        fields = ['title', 'rating', 'author', 'genre']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        author = cleaned_data.get("author")

        if self.instance.pk:
            if Book.objects.filter(title=title, author=author).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Книга з такою назвою і автором вже існує в каталозі.")
        else:
            if Book.objects.filter(title=title, author=author).exists():
                raise ValidationError("Книга з такою назвою і автором вже існує в каталозі.")

        return cleaned_data





