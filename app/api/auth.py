from flask import Blueprint, request, jsonify
# from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
# from sqlalchemy.sql.functions import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.middleware.jwt_auth import jwt_manager
from app.middleware.rate_limiter import limiter_manager

from app.models.user import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter_manager.redis_rate_limiter(auth=False, max_requests=2, window_seconds=30)
def register():
    """Register a new user"""
    data = request.get_json()

    if not data or not all(k in data for k in ["name", "email", "password"]):
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': 'Email already registered'}), 409

    new_user = User(
        name = data.get('name'),
        email = data.get('email'),
        password = generate_password_hash(data.get('password'))
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 200

@auth_bp.route('/login', methods=['POST'])
@limiter_manager.redis_rate_limiter(auth=False, max_requests=2, window_seconds=60)
def login():
    """Login a user"""
    data = request.get_json()

    if not data or not all(k in data for k in ["email", "password"]):
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({'message': 'Invalid Credentials'}), 401

    access_token = jwt_manager.create_token(str(user.id), token_type="access")
    refresh_token = jwt_manager.create_token(str(user.id), token_type="refresh")

    response = jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email
        }
    })

    response.set_cookie(
        "refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Only over HTTPS
        samesite='Strict',  # Prevent CSRF
        max_age=jwt_manager.refresh_expiry  # 7 days
    )
    return response

@auth_bp.route('/logout', methods=['POST'])
@jwt_manager.token_required(refresh=True)
@limiter_manager.redis_rate_limiter(auth=False)
def logout(user_id):
    response = jsonify({'message': 'Logged out successfully'})
    response.delete_cookie('refresh_token')
    return response

@auth_bp.route('/refresh', methods=['POST'])
@jwt_manager.token_required(refresh=True)
@limiter_manager.redis_rate_limiter(auth=False)
def refresh(user_id):
    access_token = jwt_manager.create_token(str(user_id), token_type="access")
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/profile', methods=['POST'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def profile(user_id):
    user = User.query.get(user_id)

    if not user:
        jsonify({'message': 'User not found'}), 400

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    }), 200