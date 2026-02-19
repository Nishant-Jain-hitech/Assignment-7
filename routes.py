from schemas import UpdateStudent
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Student
from schemas import UserCreate, UserLogin, StudentProfile
from auth import (
    hash_password,
    get_current_user,
    create_access_token,
    verify_password,
    require_roles,
)
from helper import check_if_teacher_id


router = APIRouter()


@router.get("/health")
def health_status():
    return {"status": "ok"}


@router.post("/create-admin")
def create_admin(db: Session = Depends(get_db)):
    db_admin = User(
        username="admin",
        email="admin@gmail.com",
        password=hash_password("12345678"),
        role="admin",
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return {"message": "Admin created!!"}


@router.post("/signup", response_model=dict)
def create_user(
    user: UserCreate,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="email already exists")

    if user.role not in ["admin", "teacher", "student"]:
        raise HTTPException(status_code=400, detail="bhai role nhi h")

    if current_user.role == "student":
        raise HTTPException(status_code=403, detail="student nhi bna sakta kuchh bhi")

    if current_user.role == "teacher" and user.role in ["admin", "teacher"]:
        raise HTTPException(
            status_code=403, detail="teacher nhi bnaega teacher/admin ko"
        )

    if user.role == "student":
        if current_user.role not in ["admin", "teacher"]:
            raise HTTPException(status_code=403, detail="bhai role sahi daal")

        creator_id = (
            current_user.id if current_user.role == "teacher" else user.created_by
        )

        if not creator_id:
            raise HTTPException(
                status_code=400, detail="created_by required for student"
            )

        if current_user.role == "teacher":
            student_count = (
                db.query(Student).filter(Student.created_by == current_user.id).count()
            )
            if student_count > 30:
                raise HTTPException(
                    status_code=403, detail="bhai 30 se jyada student nhi bna sakte"
                )
        if current_user.role == "admin":
            if not check_if_teacher_id(user.created_by, db):
                raise HTTPException(status_code=403, detail="bhai role sahi daal")

        hashed_pwd = hash_password(user.password)
        student_user = User(
            username=user.name,
            email=user.email,
            password=hashed_pwd,
            role=user.role,
        )
        db.add(student_user)
        db.flush()

        student = Student(
            name=user.name,
            grade=user.grade,
            student_user_id=student_user.id,
            created_by=creator_id,
        )

        db.add(student)
        db.commit()
        db.refresh(student)
        db.refresh(student_user)

    if user.role in ["admin", "teacher"] and current_user.role == "admin":
        hashed_pwd = hash_password(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_pwd,
            role=user.role,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    return {"user": "{} created".format(user.role)}


@router.post("/login", response_model=dict)
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="bhai user nhi h, email check kar")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/students")
def get_students(
    current_user: User = Depends(require_roles("admin")), db: Session = Depends(get_db)
):
    students = db.query(Student).all()
    return students


@router.get("/my-students",response_model=list[StudentProfile])
def get_my_students(
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db),
):
    students = db.query(Student).filter(Student.created_by == current_user.id).all()
    return students


@router.delete("/delete-student",response_model=dict)
def delete_student(
    student_user_id: int,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    student_user = (
        db.query(User)
        .filter(User.id == student_user_id, User.role == "student")
        .first()
    )
    if not student_user:
        raise HTTPException(status_code=404, detail="student nhi h to kya delete kru")

    db.delete(student_user)
    db.commit()

    return {"message": "bhaga diya bhai"}


@router.patch("/update-student",response_model=StudentProfile)
def update_student(
    student_user_id: int,
    data: UpdateStudent,
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db),
):
    if not student_user_id:
        raise HTTPException(status_code=400, detail="id daal bhai")

    db_student = (
        db.query(Student).filter(Student.student_user_id == student_user_id).first()
    )
    if not db_student:
        raise HTTPException(status_code=404, detail="bhai student nhi h")

    if current_user.role == "teacher" and db_student.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Aap doosre teacher ke student ko modify nahi kar sakte",
        )

    if data.name:
        db_student.name = data.name
    if data.grade:
        db_student.grade = data.grade

    db.commit()
    db.refresh(db_student)
    return db_student
