from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.category import CategoryOut
from app.schemas.user import UserOtherOut

class PostBase(BaseModel):
    title: str
    content: str
    image: Optional[str] = None

class PostUpdate(PostBase):
    pass

class PostCreate(PostBase):
    category_ids: List[int]

class PostOut(PostBase):
    author: UserOtherOut
    categories: List[CategoryOut]

    model_config = ConfigDict(from_attributes=True)
