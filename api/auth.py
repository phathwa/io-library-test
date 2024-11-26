from flask import request, jsonify, current_app
from functools import wraps

# Decorator to require API key for a route
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key == current_app.config["API_KEY"]:  # Fetch the API key from config
            return f(*args, **kwargs)
        return jsonify({"error": "Invalid API key"}), 401
    return decorated
