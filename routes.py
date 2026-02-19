from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session


from database import get_db
from models import User, Student
from schemas import UserCreate, UserLogin, StudentProfile
from auth import hash_password, get_current_user, create_access_token, verify_password


router = APIRouter()


@router.get("/health")
def health_status():
    return {"status": "ok"}


@router.post("/create-admin")
def create_admin(db:Session=Depends(get_db)):
    db_admin=User(username="admin",email="admin@gmail.com",password=hash_password("12345678"),role="admin")
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return {"message":"Admin created!!"}


@router.post("/signup", response_model=dict)
def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="email already exists")

    if user.role not in ["admin", "teacher", "student"]:
        raise HTTPException(status_code=400, detail="bhai role nhi h")

    if current_user.role == "teacher" and user.role == "teacher":
        raise HTTPException(status_code=403, detail="teacher nhi bnaega teacher ko")

    if user.role == "student":
        if current_user.role not in ["admin", "teacher"]:
            raise HTTPException(status_code=403, detail="bhai role sahi daal")

        if current_user.role == "teacher":
            hashed_pwd = hash_password(user.password)
            student = Student(
                name=user.name, grade=user.grade, created_by=current_user.id
            )
            db.add(student)
            db.commit()
            db.refresh(student)

            student_user = User(
                username=user.name,
                email=user.email,
                password=hashed_pwd,
                role=user.role,
            )
            db.add(student_user)
            db.commit()
            db.refresh(student_user)

        if current_user.role == "admin":
            hashed_pwd = hash_password(user.password)
            student = Student(
                name=user.name,
                grade=user.grade,
                created_by=user.created_by,
            )
            db.add(student)
            db.commit()
            db.refresh(student)

            student_user = User(
                username=user.name,
                email=user.email,
                password=hashed_pwd,
                role=user.role,
            )
            db.add(student_user)
            db.commit()
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


@router.get("/student/{student_id}", response_model=StudentProfile)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="bhai student nhi h")
    return student
