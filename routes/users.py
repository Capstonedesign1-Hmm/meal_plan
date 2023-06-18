from fastapi import APIRouter, HTTPException, status, Depends
from models.users import User, UserSignIn
from auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.hashing import get_password_hash, verify_password
from datetime import timedelta

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import database_exists, create_database

DATABASE_URL = "postgresql://admin:hmm12345@database-1.cynzq75zj9kj.us-east-1.rds.amazonaws.com/hmmDB"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("email", String, unique=True, index=True),
    Column("hashed_password", String),
)

if not database_exists(engine.url):
    create_database(engine.url)

if not engine.dialect.has_table(engine, "users"):
    metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

user_router = APIRouter(
    tags=["User"],
)

@user_router.post("/signup")
async def sign_new_user(data: User, db: Session = Depends(get_db)) -> dict:
    hashed_password = get_password_hash(data.password)
    new_user = users.insert().values(email=data.email, hashed_password=hashed_password)
    try:
        db.execute(new_user)
        db.commit()
        return {"message": "User successfully registered"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied username exists"
        )

@user_router.post("/signin")
async def sign_user_in(user: UserSignIn, db: Session = Depends(get_db)) -> dict:
    query = select(users).where(users.c.email == user.email)
    result = db.execute(query)
    user_record = result.fetchone()
    
    if user_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )
    
    if not verify_password(user.password, user_record.hashed_password):
       raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
