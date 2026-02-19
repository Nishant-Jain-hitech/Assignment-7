from database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

from models import User


def check_if_teacher_id(id:int, db:Session=Depends(get_db)):
    user=db.query(User).filter(User.id==id).first()
    if user.role=="teacher":
        return True
    return False