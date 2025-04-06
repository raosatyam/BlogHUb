from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    title: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
