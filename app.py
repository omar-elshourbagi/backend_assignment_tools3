from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re

app = Flask(__name__)
CORS(app)

api = Api(
    app,
    version='1.0',
    title='EventPlanner Phase 0 API',
    description='User Management - Sign up and Login',
    doc='/api/docs'
)

DATABASE = 'eventplanner.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("Database initialized successfully")

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 6

auth_ns = Namespace('auth', description='Authentication operations')

signup_model = api.model('SignUp', {
    'email': fields.String(required=True, description='User email address', example='user@example.com'),
    'password': fields.String(required=True, description='User password (min 6 characters)', example='password123')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email address', example='user@example.com'),
    'password': fields.String(required=True, description='User password', example='password123')
})

signup_response_model = api.model('SignUpResponse', {
    'message': fields.String(description='Success message'),
    'user_id': fields.Integer(description='Newly created user ID'),
    'email': fields.String(description='User email')
})

login_response_model = api.model('LoginResponse', {
    'message': fields.String(description='Success message'),
    'user_id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

@auth_ns.route('/signup')
class SignUp(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.response(201, 'User registered successfully', signup_response_model)
    @auth_ns.response(400, 'Invalid input', error_model)
    @auth_ns.response(409, 'Email already registered', error_model)
    @auth_ns.response(500, 'Server error', error_model)
    def post(self):
        try:
            data = api.payload
            
            if not data or not data.get('email') or not data.get('password'):
                api.abort(400, 'Email and password are required')
            
            email = data.get('email').strip().lower()
            password = data.get('password')
            
            if not validate_email(email):
                api.abort(400, 'Invalid email format')
            
            if not validate_password(password):
                api.abort(400, 'Password must be at least 6 characters long')
            
            hashed_password = generate_password_hash(password)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute(
                    'INSERT INTO users (email, password) VALUES (?, ?)',
                    (email, hashed_password)
                )
                conn.commit()
                user_id = cursor.lastrowid
                conn.close()
                
                return {
                    'message': 'User registered successfully',
                    'user_id': user_id,
                    'email': email
                }, 201
            
            except sqlite3.IntegrityError:
                conn.close()
                api.abort(409, 'Email already registered')
        
        except Exception as e:
            api.abort(500, str(e))

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login successful', login_response_model)
    @auth_ns.response(400, 'Invalid input', error_model)
    @auth_ns.response(401, 'Invalid credentials', error_model)
    @auth_ns.response(500, 'Server error', error_model)
    def post(self):
        try:
            data = api.payload
            
            if not data or not data.get('email') or not data.get('password'):
                api.abort(400, 'Email and password are required')
            
            email = data.get('email').strip().lower()
            password = data.get('password')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            conn.close()
            
            if not user or not check_password_hash(user['password'], password):
                api.abort(401, 'Invalid email or password')
            
            return {
                'message': 'Login successful',
                'user_id': user['id'],
                'email': user['email']
            }, 200
        
        except Exception as e:
            api.abort(500, str(e))

api.add_namespace(auth_ns, path='/api/auth')

@app.route('/api/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    init_db()
    print("Swagger UI available at: http://localhost:5000/api/docs")
    app.run(debug=True, port=5000)
