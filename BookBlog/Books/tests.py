from io import BytesIO
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Book, Author, Genre, Comments, Rating

User = get_user_model()


class BookAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.author = Author.objects.create(name="Author One")
        self.genre = Genre.objects.create(name="Genre One")
        self.book = Book.objects.create(
            title="Test Book",
            description="A test book description",
            author=self.author,
            genre=self.genre,
            created_by=self.user
        )

    def test_list_books(self):
        url = reverse('book-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item['id'] == self.book.id for item in response.data.get('results', [])))

    def test_create_book(self):
        url = reverse('book-list-create')
        data = {
            "title": "New Book",
            "description": "Description for new book",
            "author": {"name": self.author.name},
            "genre": {"name": self.genre.name},
            "created_by": self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_retrieve_book_detail(self):
        url = reverse('book-detail', args=[self.book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book.title)

    def test_update_book(self):
        url = reverse('book-detail', args=[self.book.id])
        data = {
            "title": "Updated Title",
            "description": "Updated description",
            "author": {"name": self.author.name},
            "genre": {"name": self.genre.name},
            "created_by": self.user.id
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Title")

    def test_delete_book(self):
        url = reverse('book-detail', args=[self.book.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)


class AuthorAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='authoruser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.author = Author.objects.create(name="Existing Author")

    def test_list_authors(self):
        url = reverse('author-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_author(self):
        url = reverse('author-list-create')
        data = {"name": "New Author"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 2)


class GenreAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='genreuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.genre = Genre.objects.create(name="Existing Genre")

    def test_list_genres(self):
        url = reverse('genre-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_genre(self):
        url = reverse('genre-list-create')
        data = {"name": "New Genre"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Genre.objects.count(), 2)


class CommentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='commentuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.author = Author.objects.create(name="Author For Comment")
        self.genre = Genre.objects.create(name="Genre For Comment")
        self.book = Book.objects.create(
            title="Book For Comment",
            description="Description",
            author=self.author,
            genre=self.genre,
            created_by=self.user
        )
        self.comment = Comments.objects.create(
            book=self.book,
            comment="Great book!",
            author=self.user
        )

    def test_list_comments(self):
        url = reverse('comment-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment(self):
        url = reverse('comment-list-create')
        data = {
            "book": self.book.id,
            "comment": "Another comment",
            "author": self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comments.objects.count(), 2)


class RatingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ratinguser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.author = Author.objects.create(name="Author For Rating")
        self.genre = Genre.objects.create(name="Genre For Rating")
        self.book = Book.objects.create(
            title="Book For Rating",
            description="Description",
            author=self.author,
            genre=self.genre,
            created_by=self.user
        )
        self.rating = Rating.objects.create(
            book=self.book,
            rating=4,
            user=self.user
        )

    def test_list_ratings(self):
        url = reverse('rating-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_rating(self):
        url = reverse('rating-list-create')
        data = {
            "book": self.book.id,
            "rating": 5,
            "user": self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)


class BookByGenreTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='genrefilter', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.genre = Genre.objects.create(name="Sci-Fi")
        self.author = Author.objects.create(name="Sci-Fi Author")
        self.book1 = Book.objects.create(
            title="Sci-Fi Book 1",
            description="Desc",
            author=self.author,
            genre=self.genre,
            created_by=self.user
        )
        self.other_genre = Genre.objects.create(name="Fantasy")
        self.book2 = Book.objects.create(
            title="Fantasy Book 1",
            description="Desc",
            author=self.author,
            genre=self.other_genre,
            created_by=self.user
        )

    def test_filter_books_by_genre(self):
        url = reverse('book-by-genre', args=[self.genre.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results', [])), 1)
        self.assertEqual(response.data.get('results')[0]['id'], self.book1.id)


class APISecurityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.protected_url = reverse('book-list-create')

    def test_authentication_required(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BookImageProcessingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='imageuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.author = Author.objects.create(name="Image Author")
        self.genre = Genre.objects.create(name="Image Genre")

    def generate_test_image(self, size=(1600, 1200), color='red'):
        buffer = BytesIO()
        image = Image.new('RGB', size, color=color)
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile("test.jpg", buffer.read(), content_type="image/jpeg")

    def test_compressed_image_dimensions(self):
        uploaded_image = self.generate_test_image()
        book = Book.objects.create(
            title="Test Book with Image",
            image=uploaded_image,
            description="Test description",
            author=self.author,
            genre=self.genre,
            created_by=self.user
        )
        compressed_url = book.compressed_image.url
        self.assertTrue(compressed_url)

        with default_storage.open(book.compressed_image.name, 'rb') as f:
            processed_image = Image.open(f)
            processed_image.load()

        self.assertEqual(processed_image.size, (800, 600))


class BookFilterAndPaginationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='filteruser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.author_a = Author.objects.create(name="Author A")
        self.author_b = Author.objects.create(name="Author B")
        self.genre_sci_fi = Genre.objects.create(name="Sci-Fi")
        self.genre_fantasy = Genre.objects.create(name="Fantasy")

        self.book1 = Book.objects.create(
            title="Book 1",
            description="Desc 1",
            author=self.author_a,
            genre=self.genre_sci_fi,
            created_by=self.user,
        )
        self.book2 = Book.objects.create(
            title="Book 2",
            description="Desc 2",
            author=self.author_a,
            genre=self.genre_sci_fi,
            created_by=self.user,
        )
        self.book3 = Book.objects.create(
            title="Book 3",
            description="Desc 3",
            author=self.author_b,
            genre=self.genre_fantasy,
            created_by=self.user,
        )
        self.book4 = Book.objects.create(
            title="Book 4",
            description="Desc 4",
            author=self.author_b,
            genre=self.genre_fantasy,
            created_by=self.user,
        )

    def test_filter_books_by_genre(self):
        url = reverse('book-list-create')
        response = self.client.get(url, {'genre': 'sci-fi'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])
        self.assertEqual(len(results), 2)
        returned_ids = set(item['id'] for item in results)
        expected_ids = {self.book1.id, self.book2.id}
        self.assertEqual(returned_ids, expected_ids)

    def test_filter_books_by_author(self):
        url = reverse('book-list-create')
        response = self.client.get(url, {'author': 'author a'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])
        self.assertEqual(len(results), 2)
        returned_ids = set(item['id'] for item in results)
        expected_ids = {self.book1.id, self.book2.id}
        self.assertEqual(returned_ids, expected_ids)

    def test_pagination(self):
        url = reverse('book-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results_page1 = response.data.get('results', [])
        self.assertEqual(len(results_page1), 3)
        response_page2 = self.client.get(url, {'page': 2})
        self.assertEqual(response_page2.status_code, status.HTTP_200_OK)
        results_page2 = response_page2.data.get('results', [])
        self.assertEqual(len(results_page2), 1)