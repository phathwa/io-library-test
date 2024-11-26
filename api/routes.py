import re
from flask import Blueprint, request, jsonify
from .models import Book
from . import db
from .auth import require_api_key
from .helpers import validate_book_data
from datetime import datetime

api_bp = Blueprint('api', __name__)

# Regular expression for a valid ISBN (13 digits)
ISBN_REGEX = r'^\d{13}$'

def validate_isbn(isbn):
    """Validate the ISBN format (must be 13 digits)."""
    if not re.match(ISBN_REGEX, isbn):
        return "Invalid ISBN format. ISBN must be 13 digits."
    return None

@api_bp.route('/books', methods=['GET', 'OPTIONS'])
@require_api_key
def get_books():
    """Get all books.
    ---
    tags:
      - Books
    responses:
      200:
        description: A list of all books
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              author:
                type: string
              isbn:
                type: string
              publish_date:
                type: string
                format: date
              created_at:
                type: string
                format: date-time
              updated_at:
                type: string
                format: date-time
    security:
      - APIKeyHeader: []  # Add security for this route
    """
    if request.method == 'OPTIONS':
      return '', 204  # Preflight response
    books = Book.query.all()
    return jsonify([{
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "publish_date": book.publish_date.strftime('%Y-%m-%d'),
        "created_at": book.created_at,
        "updated_at": book.updated_at
    } for book in books]), 200


@api_bp.route('/books/<int:id>', methods=['GET'])
@require_api_key
def get_book(id):
    """Get a specific book by ID.
    ---
    tags:
      - Books
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the book to retrieve
    responses:
      200:
        description: A specific book's details
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            author:
              type: string
            isbn:
              type: string
            publish_date:
              type: string
              format: date
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      404:
        description: Book not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
    book = db.session.get(Book, id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "publish_date": book.publish_date.strftime('%Y-%m-%d'),
        "created_at": book.created_at,
        "updated_at": book.updated_at
    }), 200

@api_bp.route('/books', methods=['POST'])
@require_api_key
def add_book():
    """Add a new book to the collection.
    ---
    tags:
      - Books
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: The title of the book
            author:
              type: string
              description: The author of the book
            isbn:
              type: string
              description: The ISBN of the book (13 digits). **ISBN must be a 13-digit number.**
            publish_date:
              type: string
              format: date
              description: The publication date in YYYY-MM-DD format
    responses:
      201:
        description: Successfully added the new book
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book added successfully"
            id:
              type: integer
              description: ID of the newly created book
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid ISBN format. ISBN must be 13 digits."
      409:
        description: ISBN already exists
        schema:
          type: object
          properties:
            error:
              type: string
              example: "ISBN already exists. Please provide a unique ISBN."
    """
    data = request.get_json()

    # Validate ISBN
    isbn_error = validate_isbn(data.get('isbn', ''))
    if isbn_error:
        return jsonify({"error": isbn_error}), 400

    # Check if the ISBN already exists in the database
    existing_book = Book.query.filter_by(isbn=data['isbn']).first()
    if existing_book:
        return jsonify({"error": "ISBN already exists. Please provide a unique ISBN."}), 409

    # Validate other fields
    error = validate_book_data(data)
    if error:
        return jsonify({"error": error}), 400

    new_book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn'],
        publish_date=datetime.strptime(data['publish_date'], '%Y-%m-%d')
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully", "id": new_book.id}), 201

@api_bp.route('/books/<int:id>', methods=['PUT'])
@require_api_key
def update_book(id):
    """Update an existing book by ID.
    ---
    tags:
      - Books
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the book to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: The updated title of the book
            author:
              type: string
              description: The updated author of the book
            isbn:
              type: string
              description: The updated ISBN of the book (13 digits). **ISBN must be a 13-digit number.**
            publish_date:
              type: string
              format: date
              description: The updated publication date in YYYY-MM-DD format
    responses:
      200:
        description: Successfully updated the book
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book updated successfully"
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid ISBN format. ISBN must be 13 digits."
      404:
        description: Book not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Book not found"
    """
    book = db.session.get(Book, id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json()

    # Validate ISBN
    if 'isbn' in data:
        isbn_error = validate_isbn(data['isbn'])
        if isbn_error:
            return jsonify({"error": isbn_error}), 400

    # Update other fields
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'isbn' in data:
        book.isbn = data['isbn']
    if 'publish_date' in data:
        try:
            book.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format for publish_date. Use YYYY-MM-DD."}), 400

    db.session.commit()
    return jsonify({"message": "Book updated successfully"}), 200

@api_bp.route('/books/<int:id>', methods=['DELETE'])
@require_api_key
def delete_book(id):
    """Delete a book by ID.
    ---
    tags:
      - Books
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the book to delete
    responses:
      200:
        description: Successfully deleted the book
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book deleted successfully"
      404:
        description: Book not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Book not found"
    """
    book = db.session.get(Book, id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 204