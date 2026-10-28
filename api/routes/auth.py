
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_id,
)
from database.connection import get_connection
from database.crud import get_user_profile

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


def normalize_email(email: str) -> str:
    email = email.strip().lower()

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid email address.",
        )

    return email


@router.post("/register", status_code=201)
def register(request: RegisterRequest):
    email = normalize_email(request.email)
    name = request.name.strip()

    if not name:
        raise HTTPException(422, "Name cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE email = %s",
            (email,),
        )
        existing = cursor.fetchone()

        if existing:
            if existing[1] is None:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "An account with this email already exists "
                        "but has no password configured. Use a secure "
                        "account recovery process before setting one."
                    ),
                )

            raise HTTPException(
                status_code=409,
                detail="An account with this email already exists.",
            )

        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (name, email, hash_password(request.password)),
        )

        user_id = cursor.fetchone()[0]
        connection.commit()

        return {
            "message": "Account created successfully.",
            "user_id": user_id,
        }

    except HTTPException:
        connection.rollback()
        raise
    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not create account.",
        )
    finally:
        cursor.close()
        connection.close()



from fastapi import Form, HTTPException

@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    email = normalize_email(username)

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

    if not user or not user[1] or not verify_password(password, user[1]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token(user[0])

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user[0]
    }


@router.get("/me")
def get_me(user_id: int = Depends(get_current_user_id)):
    profile = get_user_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=401,
            detail="User account not found.",
        )

    return profile
