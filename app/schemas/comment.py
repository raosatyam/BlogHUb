from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserOtherOut

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    pass

class PostOutForComment(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)

class CommentOut(CommentBase):
    id: int
    user: UserOtherOut
    post: PostOutForComment

    model_config = ConfigDict(from_attributes=True)
