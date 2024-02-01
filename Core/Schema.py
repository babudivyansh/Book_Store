from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class UserValidator(UserLogin):
    first_name: str
    last_name: str
    email: EmailStr
    phone: int
    location: str
