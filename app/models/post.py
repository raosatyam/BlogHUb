from app.extensions import db
from app.models.associations import post_category

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    #Relationships
    author = db.relationship("User", back_populates="posts")
    comments = db.relationship("Comment", back_populates="post", foreign_keys="Comment.post_id", cascade="all, delete-orphan")
    categories = db.relationship("Category", secondary="post_category", back_populates="posts")

