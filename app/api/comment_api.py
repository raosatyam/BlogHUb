from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.middleware.jwt_auth import jwt_manager
from app.middleware.rate_limiter import limiter_manager

from app.models.comment import Comment
from app.schemas.comment import CommentOut, CommentCreate, CommentUpdate
from app.extensions import db

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/post/<int:post_id>', methods=['GET'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def get_all_comments(post_id, *, user_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    result = [CommentOut.model_validate(comment).model_dump() for comment in comments]
    return jsonify(result), 200

@comment_bp.route('/<int:comment_id>', methods=['GET'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def get_comment(comment_id, *, user_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'message': 'Comment not found'}), 404

    return jsonify(CommentOut.model_validate(comment).model_dump()), 200

@comment_bp.route('/post/<int:post_id>', methods=['POST'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def create_comment(post_id, *, user_id):
    try:
        data = CommentCreate(**request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Invalid data', 'errors': e.errors()}), 400

    new_comment = Comment(
        content=data.content,
        user_id=user_id,
        post_id=post_id
    )
    db.session.add(new_comment)
    db.session.commit()
    result = CommentOut.model_validate(new_comment).model_dump()
    result.update({'message': 'Comment created successfully'})
    return jsonify(result), 200

@comment_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def update_comment(comment_id, *, user_id):
    try:
        data = CommentUpdate(**request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Invalid data', 'errors': e.errors()}), 400

    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'message': 'Comment not found'}), 404
    if comment.user_id != user_id:
        return jsonify({'message': 'Unauthorized: Cannot update another user\'s comment'}), 403

    comment.content = data.content
    db.session.commit()
    return {'message': 'Comment updated successfully'}, 200

@comment_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_manager.token_required()
@limiter_manager.redis_rate_limiter()
def delete_comment(comment_id, *, user_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'message': 'Comment not found'}), 404
    if comment.user_id != user_id:
        return jsonify({'message': 'Unauthorized: Cannot delete another user\'s comment'}), 403

    db.session.delete(comment)
    db.session.commit()
    return {'message': 'Comment deleted successfully'}, 200
