from datetime import datetime

def validate_book_data(data):
    required_fields = ["title", "author", "isbn", "publish_date"]
    for field in required_fields:
        if field not in data:
            return f"Missing field: {field}"
    try:
        datetime.strptime(data['publish_date'], '%Y-%m-%d')
    except ValueError:
        return "Invalid date format for publish_date. Use YYYY-MM-DD."
    return None
