from pydantic import BaseModel

class Character(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True  
