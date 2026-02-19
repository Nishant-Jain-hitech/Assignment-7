from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: Optional[str] | None = None
    email: Optional[EmailStr] | None = None
    password: Optional[str] | None = None
    role: str
    name: Optional[str] | None = None
    grade: Optional[str] | None = None
    created_by: Optional[int] | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class StudentProfile(BaseModel):
    id: int
    student_user_id:int
    name: str
    grade: str
    created_by: int


class UpdateStudent(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
