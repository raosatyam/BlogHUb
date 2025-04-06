import json
from datetime import datetime, UTC
from flask import Blueprint, request, jsonify, make_response
from pydantic import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

from app.middleware.jwt_auth import jwt_manager
from app.middleware.rate_limiter import limiter_manager

from app.models.user import User
from app.extensions import db
from app.schemas.user import UserCreate, UserLogIn, UserOut

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter_manager.redis_rate_limiter(auth=False, max_requests=4, window_seconds=30)
def register():
    """Register a new user"""
    try:
        data = UserCreate(**request.get_json())
    except ValidationError as e:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'errors': e.errors()[0]['msg']
        }), 400)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Invalid request format',
            'errors': str(e)
        }), 400

    if User.query.filter_by(email=data.email).first():
        return jsonify({'message': 'Email already registered'}), 409

    new_user = User(
        name = data.name,
        email = data.email,
        password = generate_password_hash(data.password)
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
@limiter_manager.redis_rate_limiter(auth=False, max_requests=10, window_seconds=60)
def login():
    """Login a user"""
    try:
        data = UserLogIn(**request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Invalid data', 'errors': e.errors()}), 400

    user = User.query.filter_by(email=data.email).first()
    if not user or not check_password_hash(user.password, data.password):
        return jsonify({'message': 'Invalid Credentials'}), 401

    access_token = jwt_manager.create_token(str(user.id), token_type="access")
    refresh_token = jwt_manager.create_token(str(user.id), token_type="refresh")

    response = jsonify({
        'message': 'Login Successful',
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
    user.last_login = datetime.now(UTC)
    db.session.commit()

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

@auth_bp.route('/profile', methods=['GET'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def profile(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'user': UserOut.model_validate(user).model_dump()
    }), 200
