from pydantic import BaseModel
from typing import Optional, List
from app.schemas.category import CategoryOut
from app.schemas.user import UserOut

class PostBase(BaseModel):
    title: str
    content: str
    image: Optional[str] = None

class PostCreate(PostBase):
    user_id: int
    category_id: int
    tags: Optional[List[int]] = []

class PostOut(PostBase):
    id: int
    author: UserOut
    category: CategoryOut

    class Config:
        orm_model = True
