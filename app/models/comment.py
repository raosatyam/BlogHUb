from app.extensions import db
from sqlalchemy.orm import relationship

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, index=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    #Relationship
    user = db.relationship("User", back_populates="comments", foreign_keys=[user_id])
    post = db.relationship("Post", back_populates="comments", foreign_keys=[post_id])
