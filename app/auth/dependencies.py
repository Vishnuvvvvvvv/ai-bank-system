from fastapi import Depends, HTTPException

from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user import User

from app.auth.jwt_handler import (
    SECRET_KEY,
    ALGORITHM
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials"
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user