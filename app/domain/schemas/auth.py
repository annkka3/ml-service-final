
from pydantic import BaseModel, EmailStr

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProfileOut(BaseModel):
    id: str
    email: EmailStr

class SignResponse(BaseModel):
    id: str
    user_id: str
    email: EmailStr
    message: str = "Registered"

class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class UserAuth(BaseModel):
    email: EmailStr
    password: str
