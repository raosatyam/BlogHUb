from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.middleware.jwt_auth import jwt_manager
from app.middleware.rate_limiter import limiter_manager

from app.extensions import db
from app.schemas.category import CategoryOut, CategoryCreate, CategoryUpdate
from app.models.category import Category
from app.models.post import Post

category_bp = Blueprint('category', __name__)

@category_bp.route('/all', methods=['GET'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def get_all_categories(user_id):
    categories = Category.query.all()
    result = [CategoryOut.model_validate(category).model_dump() for category in categories]
    return jsonify(result), 200

@category_bp.route('/post/<int:post_id>', methods=['GET'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def get_post_categories(post_id, *,user_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    categories = post.categories
    result = [CategoryOut.model_validate(category).model_dump() for category in categories]
    return jsonify(result), 200


@category_bp.route('/<int:category_id>', methods=['GET'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def get_category(category_id, *,user_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": 'Category not found'}), 404

    result = CategoryOut.model_validate(category).model_dump()
    return jsonify(result), 200


@category_bp.route('/', methods=['POST'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def create_category(user_id):
    try:
        data = CategoryCreate(**request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Invalid data', 'errors': e.errors()}), 400

    new_category = Category(
        title=data.title
    )
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category created successfully'}), 200

@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def update_category(category_id, *, user_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": 'Category not found'}), 404

    try:
        data = CategoryUpdate(**request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Invalid data', 'errors': e.errors()}), 400

    category.title = data.title
    db.session.commit()

    return jsonify({'message': 'Category updated successfully'}), 200

@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def delete_category(category_id, *, user_id):

    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": 'Category not found'}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Category deleted successfully'}), 200