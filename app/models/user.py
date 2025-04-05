from app.extensions import db
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255), index=True, nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    about = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(255), nullable=False)

    # posts = relationship("Post", back_populates="author")
    # comments = relationship("Comment", back_populates="user")