from datetime import datetime
import re

def validate_book_data(data):
    """
    Validate book data for required fields and empty string values.

    Args:
        data (dict): The input data for the book.

    Returns:
        str: An error message if validation fails, or None if validation succeeds.
    """
    required_fields = ['title', 'author', 'isbn', 'publish_date']

    for field in required_fields:
        value = data.get(field)
        if value is None or value.strip() == "":
            return f"The field '{field}' is required and cannot be empty."

    # Additional validation for specific fields
    if not isinstance(data.get('isbn', ''), str) or len(data['isbn']) != 13 or not data['isbn'].isdigit():
        return "Invalid ISBN format. ISBN must be a 13-digit number."

    if 'publish_date' in data:
        try:
            datetime.strptime(data['publish_date'], '%Y-%m-%d')
        except ValueError:
            return "Invalid date format for 'publish_date'. Use YYYY-MM-DD."

    return None

def validate_isbn(isbn):
    """Validate the ISBN format (must be 13 digits)."""
    # Regular expression for a valid ISBN (13 digits)
    ISBN_REGEX = r'^\d{13}$'
    if not isbn.strip():  # Check for empty or whitespace-only string
        return "ISBN cannot be empty."
    if not re.match(ISBN_REGEX, isbn):
        return "Invalid ISBN format. ISBN must be 13 digits."
    return None