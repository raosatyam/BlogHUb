from app.extensions import db
from datetime import datetime, UTC

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255), index=True, nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    about = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    posts = db.relationship("Post", back_populates="author", foreign_keys="Post.user_id", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="user", foreign_keys="Comment.user_id" , cascade="all, delete-orphan")
