from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserLogin(BaseModel):
    username: str
    password: str


class UserValidator(UserLogin):
    model_config = ConfigDict(from_attributes=True)
    first_name: str
    last_name: str
    email: EmailStr
    phone: int
    location: str
    is_superuser: Optional[str] = None


class BookValidator(BaseModel):
    book_name: str
    author: str
    price: int
    quantity: int
