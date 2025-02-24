from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from Users.models import CustomUser
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    average_rating = models.FloatField(null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='images')

    compressed_image = ImageSpecField(
        source='image',
        processors=[ResizeToFill(800, 600)],
        format='JPEG',
        options={'quality': 80},
    )

    def __str__(self):
        return self.title

    def calculate_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            avg_rating = ratings.aggregate(models.Avg('rating'))['rating__avg']
            self.average_rating = avg_rating
        else:
            self.average_rating = None
        self.save(update_fields=['average_rating'])


class Comments(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} - {self.book.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.book.calculate_rating()


class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user} - {self.book.title}: {self.rating}"

    def clean(self):
        if self.rating > 10:
            raise ValidationError("Оцінка не може бути більше 10.")
        if self.rating < 1:
            raise ValidationError("Оцінка не може бути менше 1.")





