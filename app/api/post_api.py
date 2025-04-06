
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.middleware.jwt_auth import jwt_manager
from app.middleware.rate_limiter import limiter_manager

from app.models.post import Post
from app.models.category import Category
from app.extensions import db
from app.schemas.post import PostCreate, PostOut, PostUpdate

post_bp = Blueprint('post', __name__)

@post_bp.route('/all', methods=['GET'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def get_all_posts(*, user_id):
    posts = Post.query.all()
    return jsonify([PostOut.model_validate(post).model_dump() for post in posts])

@post_bp.route('/<int:post_id>', methods=['GET'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def get_post(post_id, *, user_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    return jsonify(PostOut.model_validate(post).model_dump())

@post_bp.route('/', methods=['POST'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def create_post(*, user_id):
    try:
        data = PostCreate(**request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Invalid data', 'errors': e.errors()}), 400

    new_post = Post(
        title=data.title,
        content=data.content,
        user_id=user_id
    )
    categories = Category.query.filter(Category.id.in_(data.category_ids)).all()
    new_post.categories = categories
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'Post created successfully'}), 200

@post_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def update_post(post_id, *, user_id):
    try:
        data = PostUpdate(**request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Invalid data', 'errors': e.errors()}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    if post.user_id != user_id:
        return jsonify({'message': 'Unauthorized: Cannot update another user\'s post'}), 403

    post.title = data.title
    post.content = data.content
    db.session.commit()
    return {'message': 'Post updated successfully'}, 200

@post_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def delete_post(post_id, *, user_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    if post.user_id != user_id:
        return jsonify({'message': 'Unauthorized: Cannot delete another user\'s post'}), 403

    db.session.delete(post)
    db.session.commit()
    return {'message': 'Post deleted successfully'}, 200
