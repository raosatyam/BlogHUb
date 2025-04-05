from pydantic import BaseModel
from app.schemas.post import PostOut
from app.schemas.user import UserOut

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    user_id: int
    post_id: int

class CommentOut(CommentBase):
    id: int
    user: UserOut
    post: PostOut

    class Config:
        orm_mode = True