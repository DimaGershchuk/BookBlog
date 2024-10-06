from rest_framework import serializers
from .models import Book, Author, Genre, Comments, Rating
from Users.models import CustomUser


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  # Для відображення імені автора коментаря

    class Meta:
        model = Comments
        fields = ['id', 'author', 'comment', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Виводить ім'я користувача, а не ID

    class Meta:
        model = Rating
        fields = ['id', 'user', 'rating']


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()  # Вкладений серіалізатор для автора
    genre = GenreSerializer()  # Вкладений серіалізатор для жанру
    reviews = CommentSerializer(many=True, read_only=True)  # Вкладений серіалізатор для коментарів
    ratings = RatingSerializer(many=True, read_only=True)  # Вкладений серіалізатор для рейтингів

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'created_by', 'description', 'average_rating', 'reviews', 'ratings']

    def create(self, validated_data):
        author_data = validated_data.pop('author')
        genre_data = validated_data.pop('genre')
        author, created = Author.objects.get_or_create(**author_data)
        genre, created = Genre.objects.get_or_create(**genre_data)
        book = Book.objects.create(author=author, genre=genre, **validated_data)

        return book

    def update(self, instance, validated_data):
        author_data = validated_data.pop('author')
        genre_data = validated_data.pop('genre')

        author, created = Author.objects.get_or_create(**author_data)
        genre, created = Genre.objects.get_or_create(**genre_data)

        instance.author = author
        instance.genre = genre
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        return instance
