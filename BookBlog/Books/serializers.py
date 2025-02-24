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
    author = serializers.StringRelatedField(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Comments
        fields = ['id', 'book', 'author', 'comment', 'created_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Rating
        fields = ['id', 'book', 'user', 'rating',]

    def create(self, validated_data):
        user = self.context['request'].user
        book = validated_data.get('book')
        rating, created = Rating.objects.update_or_create(
            user=user,
            book=book,
            defaults={'rating': validated_data.get('rating')}
        )
        return rating


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    genre = GenreSerializer()
    reviews = CommentSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'created_by', 'description',
                  'average_rating', 'reviews', 'ratings', 'image']

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

        if 'image' in validated_data:
            instance.image = validated_data.get('image')

        instance.save()

        return instance
