from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.hash import bcrypt
from database_con import SessionLocal, Base, engine
from sqlalchemy import Column, Integer, String
from passlib.context import CryptContext
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
# Database model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    age = Column(Integer)  # Added age field
    full_name = Column(String)
 
# Pydantic schema for user creation
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    age: int = Field(..., ge=0)  # Added age field
    full_name: str
 
# Pydantic schema for user response (what is returned after creation/login)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    age: int  # Added age field
    full_name: str
 
    class Config:
        orm_mode = True # Enables ORM mode for Pydantic to read from SQLAlchemy models
 
# Pydantic schema for user login
class UserLogin(BaseModel):
    username_or_email: str # Field to accept either username or email
    password: str
 
# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)
 
router = APIRouter()
 
# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db # Provides a database session to the endpoint function
    finally:
        db.close() # Ensures the session is closed after the request is processed
 
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the database.
    Checks if email or username already exists before creating.
    Hashes the password before storing.
    """
    # Check if email is already registered
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # Check if username is already taken
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
 
    # Hash the user's password using bcrypt
    hashed_password = pwd_context.hash(user.password)
    
    # Create a new User object with provided data
    new_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
        age=user.age, # Assign the age from the request
        full_name=user.full_name
    )
    
    # Add the new user to the database session, commit, and refresh to get the ID
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user # Return the newly created user data
 
@router.post("/login", response_model=UserResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user based on username/email and password.
    Returns user data upon successful login, raises HTTPException otherwise.
    """
    # Find user by email OR username
    user = db.query(User).filter(
        (User.email == login_data.username_or_email) | # Check by email
        (User.username == login_data.username_or_email) # Check by username
    ).first()
 
    # If user not found or password does not match, raise 401 Unauthorized
    if not user or not pwd_context.verify(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
 
    return user # Return the authenticated user data
