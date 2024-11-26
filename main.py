from flask import jsonify, redirect, render_template, request, url_for, current_app
from dotenv import load_dotenv
from flask_cors import CORS
from api import create_app, db
import os

# Load environment variables from .env file
# load_dotenv()

# Use "development" as fallback
app = create_app(os.getenv("FLASK_ENV", "development")) 

# default routes, not related to endpoints (TODO maybe should move to routes.py)
@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')

@app.route('/api', methods=['GET'])
def api_landing():
    return redirect(url_for("app.main")) 

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "Content-Type,Authorization,X-API-Key"}})

@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key')
        return response, 204

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
    app.run(debug=True, host='0.0.0.0', port=80)
