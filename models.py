from sqlalchemy import ForeignKey, Enum as SQLAlchemyEnum
from database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from enum import Enum

class UserRole(str,Enum):
    ADMIN="admin"
    TEACHER="teacher"
    STUDENT="student"


class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True, index=True)
    username:Mapped[str]=mapped_column(nullable=False)
    email:Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password:Mapped[str] = mapped_column(nullable=False)
    role:Mapped[UserRole]=mapped_column(SQLAlchemyEnum(UserRole),nullable=False)
    
    student=relationship("Student",back_populates="users",cascade="all, delete-orphan")


class Student(Base):
    __tablename__="students"
    
    id:Mapped[int] = mapped_column(primary_key=True, index=True)
    name:Mapped[str]=mapped_column(nullable=False)
    grade:Mapped[str]=mapped_column(nullable=False)
    
    created_by:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    
    users=relationship("User",back_populates="student")
    
    