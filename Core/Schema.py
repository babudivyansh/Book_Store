from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserLogin(BaseModel):
    username: str = Field(default='Enter user name', title='Enter User name')
    password: str = Field(default='Enter user password', title='Enter User password', min_length=8)


class UserValidator(UserLogin):
    model_config = ConfigDict(from_attributes=True)
    first_name: str = Field(default='Enter First Name', title='Enter First Name', pattern=r"^[A-Z]{1}\D{3,}$")
    last_name: str = Field(default='Enter Last Name', title='Enter Last Name', pattern=r"^[A-Z]{1}\D{3,}$")
    email: EmailStr = Field(default='Enter Email', title='Enter Email')
    phone: int = Field(default='Enter Phone Number', title='Enter Phone Number')
    location: str = Field(default='Enter Location', title='Enter Location')
    super_key: Optional[str] = None


class BookValidator(BaseModel):
    book_name: str = Field(default='Enter Book Name', title='Enter Book Name')
    author: str = Field(default='Enter Author Name', title='Enter Author Name')
    price: int = Field(default='Enter Price', title='Enter Price')
    quantity: int = Field(default='Enter Email', title='Enter Quantity')


class CartItemsValidator(BaseModel):
    book_id: int = Field(default='Enter Book Id', title='Enter Book Id')
    quantity: int = Field(default='Enter Quantity', title='Enter Quantity')


