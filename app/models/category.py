from app.extensions import db

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(255), unique=True, index=True, nullable=False)

    #Relationships
    posts = db.relationship("Post", secondary="post_category" ,back_populates="categories")
