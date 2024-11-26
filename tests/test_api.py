import unittest
from unittest.mock import patch
from main import app, db
from api.models import Book  # Import your Book model

class TestBookAPI(unittest.TestCase):
    def setUp(self):
        """Set up the test client and mock the get_public_ip function."""
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            # Drop and recreate all tables to ensure a clean state for each test
            db.drop_all()
            db.create_all()

        # Mocking get_public_ip to return a dummy IP during tests
        patch('setup_public_ip.get_public_ip', return_value='127.0.0.1').start()

    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_book(self):
        """Test the addition of a new book."""
        response = self.app.post('/api/books', json={
            "title": "Unique Test Book",
            "author": "Author Name",
            "isbn": "9876543210987",  # Use a unique ISBN
            "publish_date": "2024-01-01"
        }, headers={"X-API-Key": "fake-key"})
        self.assertEqual(response.status_code, 201)

    def test_get_books(self):
        """Test retrieving the list of books."""
        response = self.app.get('/api/books', headers={"X-API-Key": "fake-key"})
        self.assertEqual(response.status_code, 200)

    def test_invalid_auth(self):
        """Test invalid authentication with the wrong API key."""
        response = self.app.get('/api/books', headers={"X-API-Key": "invalid-api-key"})
        self.assertEqual(response.status_code, 401)

    def test_update_book(self):
        """Test updating an existing book."""
        # First, add a book to update
        response = self.app.post('/api/books', json={
            "title": "Test Book for Update",
            "author": "Author Name",
            "isbn": "1122334455667",
            "publish_date": "2024-01-01"
        }, headers={"X-API-Key": "fake-key"})
        book_id = response.json['id']

        # Now update the book
        response = self.app.put(f'/api/books/{book_id}', json={
            "title": "Updated Book",
            "author": "Updated Author",
            "isbn": "1122334455667",  # Keeping the ISBN same for the update
            "publish_date": "2025-01-01"
        }, headers={"X-API-Key": "fake-key"})
        self.assertEqual(response.status_code, 200)

    def test_delete_book(self):
        """Test deleting an existing book."""
        # First, add a book to delete
        response = self.app.post('/api/books', json={
            "title": "Test Book for Deletion",
            "author": "Author Name",
            "isbn": "2233445566778",
            "publish_date": "2024-01-01"
        }, headers={"X-API-Key": "fake-key"})
        book_id = response.json['id']

        # Now delete the book
        response = self.app.delete(f'/api/books/{book_id}', headers={"X-API-Key": "fake-key"})
        self.assertEqual(response.status_code, 204)  # No Content response
    
    # Edge Case 1: Retrieving Books When the Database is Empty
    def test_get_books_empty_db(self):
        """Test retrieving books when no books exist in the database."""
        with app.app_context():
            # Ensure database is empty before the test
            db.session.remove()
            db.drop_all()
            db.create_all()

        response = self.app.get('/api/books', headers={"X-API-Key": "fake-key"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])  # Should return an empty list

    # Edge Case 2: Adding a Book with Invalid Data (Malformed ISBN)
    def test_add_book_invalid_data(self):
        """Test adding a book with invalid data (e.g., incorrect ISBN)."""
        response = self.app.post('/api/books', json={
            "title": "Invalid Book",
            "author": "Invalid Author",
            "isbn": "invalidisbn",  # Invalid ISBN format
            "publish_date": "2024-01-01"
        }, headers={"X-API-Key": "fake-key"})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)  # Ensure error is returned

    # Edge Case 3: Adding a Book with a Duplicate ISBN
    def test_add_book_duplicate_isbn(self):
        """Test adding a book with a duplicate ISBN."""
        # First, add a book with a unique ISBN
        response = self.app.post('/api/books', json={
            "title": "Original Book",
            "author": "Original Author",
            "isbn": "1234567890123",
            "publish_date": "2024-01-01"
        }, headers={"X-API-Key": "fake-key"})
        self.assertEqual(response.status_code, 201)

        # Try adding another book with the same ISBN
        response = self.app.post('/api/books', json={
            "title": "Duplicate Book",
            "author": "Another Author",
            "isbn": "1234567890123",  # Same ISBN as above
            "publish_date": "2025-01-01"
        }, headers={"X-API-Key": "fake-key"})
        self.assertEqual(response.status_code, 409)  # Conflict status code
        self.assertIn('error', response.json)  # Ensure error is returned
        self.assertIn('ISBN already exists', response.json['error'])

if __name__ == '__main__':
    unittest.main()
