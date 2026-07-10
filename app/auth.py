# from datetime import datetime, timedelta
# from typing import Optional
# from jose import jwt, JWTError
# from passlib.context import CryptContext
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from app.config import settings
# from app.database import db
# from app.schemas import UserOut
# from app.models import UserRole
# from bson import ObjectId
# from dotenv import load_dotenv
# # from auth import ALGORITHM, SECRET_KEY
# import os

# print("JWT_EXP_MINUTES from settings:", settings.JWT_EXP_MINUTES)

# # Load the .env file
# load_dotenv()

# # Access the environment variables
# SECRET_KEY = os.getenv("JWT_SECRET")
# ALGORITHM = os.getenv("JWT_ALGORITHM","HS256")
# # ACCESS_TOKEN_EXPIRES_IN = os.getenv("ACCESS_TOKEN_EXPIRES_IN",30)  # minutes
# # REFRESH_TOKEN_EXPIRES_IN = os, getenv("REFRESH_TOKEN_EXPIRES_IN",1440)  # 1 day


# # Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # OAuth2 token scheme (used in Authorization header)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# # def verify_password(plain: str, hashed: str) -> bool:
# #     return pwd_context.verify(plain, hashed)


# def create_access_token(subject: str, expires_delta: Optional[timedelta] = None):
#     """Create JWT access token with expiration"""
#     to_encode = {"sub": subject}
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXP_MINUTES))
#     print("Token will expire at (UTC):", expire)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


# # ---------------------------
# # User fetching helpers
# # ---------------------------

# async def get_user_by_email(email: str):
#     return await db["users"].find_one({"email": email})


# async def get_user_by_id(user_id: str):
#     try:
#         return await db["users"].find_one({"_id": ObjectId(user_id)})
#     except Exception:
#         return None


# async def authenticate_user(email: str, password: str):
#     user = await db["users"].find_one({"email": email})
#     if not user:
#         return None
        
#     if not verify_password(password, user["password_hash"]):
#         return None
        
#     return user

# # ---------------------------
# # Current user retrieval
# # ---------------------------

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     """Extract and validate JWT token, return user"""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     user = await get_user_by_id(user_id)
#     if user is None:
#         raise credentials_exception
#     return user


# def require_role(required_role: str):
#     async def role_dependency(current_user: dict = Depends(get_current_user)) -> dict:
#         if current_user.get("role") != required_role:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Insufficient permissions"
#             )
#         return current_user
#     return role_dependency

# def require_tracking_access():
#     """Dependency for users with tracking access (admin or tracking_view)"""
#     async def access_checker(current_user: UserOut = Depends(get_current_user)):
#         if current_user.role not in [UserRole.ADMIN, UserRole.TRACKING_VIEW]:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Requires tracking access"
#             )
#         return current_user
#     return access_checker


# def decode_access_token(token: str):
#     """Decode a JWT token and return its payload."""
#     try:
#         payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired"
#         )
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token"
#         )


# app/jwt_token.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.database import db
from app.schemas import UserOut
from app.models import UserRole
from bson import ObjectId
import logging
import enum

# Configure logger
logger = logging.getLogger(__name__)

# Debug: Check settings
logger.info(f"JWT_EXP_MINUTES from settings: {settings.JWT_EXP_MINUTES}")
logger.info(f"JWT_SECRET length: {len(settings.JWT_SECRET) if settings.JWT_SECRET else 0}")
logger.info(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token scheme (used in Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_access_token(
    subject: str, 
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
) -> str:
    """Create JWT access token with expiration"""
    to_encode = {"sub": subject, "type": token_type}
    
    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXP_MINUTES)
    
    logger.debug(f"Token will expire at (UTC): {expire}")
    to_encode.update({"exp": expire})
    
    # Encode token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    logger.debug(f"Created {token_type} token for subject: {subject}")
    return encoded_jwt


def create_password_reset_token(user_id: str) -> str:
    """Create a short-lived password reset token"""
    expires_delta = timedelta(minutes=15)  # Reset tokens expire in 15 minutes
    return create_access_token(
        subject=user_id,
        expires_delta=expires_delta,
        token_type="password_reset"
    )


# ---------------------------
# User fetching helpers
# ---------------------------

async def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email address"""
    try:
        user = await db["users"].find_one({"email": email})
        if user and "_id" in user:
            user["id"] = str(user["_id"])
        return user
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        return None


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by MongoDB ID"""
    try:
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if user and "_id" in user:
            user["id"] = str(user["_id"])
        return user
    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {e}")
        return None


async def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user with email and password"""
    try:
        user = await get_user_by_email(email)
        if not user:
            logger.warning(f"Authentication failed: No user with email {email}")
            return None
            
        if not verify_password(password, user.get("password_hash", "")):
            logger.warning(f"Authentication failed: Wrong password for {email}")
            return None
            
        logger.info(f"Authentication successful for user: {email}")
        return user
    except Exception as e:
        logger.error(f"Authentication error for {email}: {e}")
        return None


# ---------------------------
# Token validation and user retrieval
# ---------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Extract and validate JWT token, return user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        
        if user_id is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception
            
        if token_type != "access":
            logger.warning(f"Wrong token type: {token_type}")
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise credentials_exception

    user = await get_user_by_id(user_id)
    if user is None:
        logger.warning(f"User not found for ID: {user_id}")
        raise credentials_exception
        
    logger.debug(f"Authenticated user: {user.get('email')}")
    return user


def decode_access_token(token: str) -> dict:
    """Decode a JWT token and return its payload."""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise jwt.ExpiredSignatureError("Token has expired")
            
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired in decode_access_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError as e:
        logger.warning(f"Invalid token in decode_access_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def decode_password_reset_token(token: str) -> str:
    """Decode and validate password reset token"""
    try:
        payload = decode_access_token(token)
        
        # Check token type
        token_type = payload.get("type", "")
        if token_type != "password_reset":
            logger.warning(f"Wrong token type for password reset: {token_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Password reset token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
            
        logger.info(f"Password reset token decoded for user: {user_id}")
        return user_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error decoding password reset token: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )


# ---------------------------
# Role-based access control
# ---------------------------

def require_role(required_role: str):
    """Dependency for role-based access control"""
    async def role_dependency(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        
        if user_role != required_role:
            logger.warning(
                f"Access denied: User {current_user.get('email')} has role {user_role}, "
                f"required {required_role}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        logger.debug(f"Role check passed for {current_user.get('email')}")
        return current_user
    return role_dependency


def require_tracking_access():
    """Dependency for users with tracking access (admin or tracking_view)"""
    async def access_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        # Convert UserRole enum if needed
        if hasattr(UserRole, 'ADMIN'):
            admin_role = UserRole.ADMIN.value if isinstance(UserRole.ADMIN, enum.Enum) else UserRole.ADMIN
            tracking_role = UserRole.TRACKING_VIEW.value if isinstance(UserRole.TRACKING_VIEW, enum.Enum) else UserRole.TRACKING_VIEW
        else:
            admin_role = "admin"
            tracking_role = "tracking_view"
        
        if user_role not in [admin_role, tracking_role]:
            logger.warning(
                f"Tracking access denied for user: {current_user.get('email')} with role {user_role}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requires tracking access"
            )
            
        logger.debug(f"Tracking access granted for {current_user.get('email')}")
        return current_user
    return access_checker


# ---------------------------
# Utility functions
# ---------------------------

async def validate_password_reset_token(token: str) -> Optional[dict]:
    """Validate password reset token and return user if valid"""
    try:
        # First, try to decode as JWT password reset token
        try:
            user_id = decode_password_reset_token(token)
            user = await get_user_by_id(user_id)
            if user:
                logger.info(f"Password reset JWT token validated for user: {user.get('email')}")
                return user
        except Exception:
            # Not a JWT token or decode failed; fall back to DB-stored token (OTP)
            from app.crud import get_password_reset_token
            token_doc = await get_password_reset_token(token)
            if not token_doc:
                logger.warning("No password reset token found in DB for token")
                return None
            # Check expiry and used flag handled by get_password_reset_token query
            user = await get_user_by_id(token_doc.get("user_id"))
        
            if not user:
                logger.warning(f"User not found for reset token user_id: {token_doc.get('user_id')}")
                return None
            logger.info(f"Password reset OTP token validated for user: {user.get('email')}")
            return user
        
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"Error validating password reset token: {e}")
        return None