from fastapi import APIRouter, HTTPException, status
from models.users import User, UserSignIn
from auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.hashing import get_password_hash, verify_password
from datetime import timedelta

user_router = APIRouter(
    tags=["User"],
)
users = {}

@user_router.post("/signup")
async def sign_new_user(data: User) -> dict:
    if data.email in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied username exists"
        )
    hashed_password = get_password_hash(data.password)
    users[data.email] = User(email=data.email, password=hashed_password)
    return {
        "message": "User successfully registered"
    }

@user_router.post("/signin")
async def sign_user_in(user: UserSignIn) -> dict:
    if user.email not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )
    stored_user = users[user.email]
    if not verify_password(user.password, stored_user.password):
       raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
