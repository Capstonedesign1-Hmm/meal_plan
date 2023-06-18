from pydantic import BaseModel, EmailStr
from typing import Optional, List

class User(BaseModel):
    email : EmailStr
    password : str

class UserSignIn(BaseModel):
    email : EmailStr
    password : str

    class Config:
        schema_extra = {
            "example": {
                "email": "exmaple@gmail.com",
                "password": "example1!"
            }
        }