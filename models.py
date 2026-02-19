from sqlalchemy import ForeignKey, Enum as SQLAlchemyEnum
from database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLAlchemyEnum(UserRole), nullable=False)

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="user_account",
        cascade="all, delete-orphan",
        uselist=False,
        foreign_keys="Student.student_user_id",
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    grade: Mapped[str] = mapped_column(nullable=False)

    student_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    user_account: Mapped["User"] = relationship(
        "User", back_populates="student", foreign_keys=[student_user_id]
    )

    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
