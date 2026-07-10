from fastapi import APIRouter, Depends, HTTPException
from app.database import get_user_by_email, db
from app.schemas import Token, UserCreate, UserOut, LoginRequest, ForgotPasswordSchema
from app.auth import (
    authenticate_user,
    create_access_token,
    create_password_reset_token,
    validate_password_reset_token,
    hash_password,
    require_role,
    decode_access_token,
)
from datetime import datetime, timedelta
from pydantic import BaseModel
from bson import ObjectId
from fastapi import Body
from fastapi.security import OAuth2PasswordRequestForm
#added imports
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.services.email_service import email_service
# In app/routes/auth.py
import logging

# Add this line after imports
logger = logging.getLogger(__name__)

# Your existing imports...
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import random
from typing import Optional
from app.services.email_service import email_service
from app.crud import (
    find_user_by_email,
    store_password_reset_token,
    mark_password_reset_token_used,
    update_user_password,
)
# For optional MX/domain checks (best-effort)
try:
    import dns.resolver  # type: ignore
except Exception:
    dns = None
# ... rest of your imports

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    # Quick syntactic validation (Pydantic already validates EmailStr)

    # Optional: Check domain MX records to reduce invalid/non-deliverable emails
    def domain_has_mx(email: str) -> bool:
        if not dns:
            logger.debug("dnspython not available; skipping MX check")
            return True
        try:
            domain = email.split("@", 1)[1]
            answers = dns.resolver.resolve(domain, 'MX')
            return len(answers) > 0
        except Exception as e:
            logger.debug(f"MX lookup failed for domain of {email}: {e}")
            return False

    # 1️⃣ Check if user already exists
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # If MX check was performed and failed, reject the registration
    if not domain_has_mx(user.email):
        raise HTTPException(status_code=400, detail="Email domain looks invalid or has no MX records")

    # 2️⃣ Create user with email_verified = False
    user_dict = {
        "email": user.email,
        "password_hash": hash_password(user.password),
        "role": user.role,
        "email_verified": False,   # 👈 IMPORTANT
        "created_at": datetime.utcnow()
    }

    result = await db["users"].insert_one(user_dict)
    user_id = str(result.inserted_id)

    # 3️⃣ Generate 6-digit OTP
    otp = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # 4️⃣ Store OTP in DB (email verification)
    await db["email_verification_tokens"].insert_one({
        "user_id": user_id,
        "otp": otp,
        "expires_at": expires_at,
        "used": False,
        "created_at": datetime.utcnow()
    })

    # 5️⃣ Send OTP email (best-effort). Use existing OTP sender for now.
    send_ok = False
    try:
        # Prefer a verification-specific method if present, otherwise reuse password-reset OTP sender
        if hasattr(email_service, 'send_email_verification_otp'):
            send_ok = await email_service.send_email_verification_otp(
                to_email=user.email,
                otp=otp,
                user_name=user.email.split("@")[0],
                expiry_minutes=10
            )
        else:
            send_ok = await email_service.send_password_reset_otp(
                to_email=user.email,
                otp=otp,
                user_name=user.email.split("@")[0],
                expiry_minutes=10
            )
    except Exception as e:
        logger.error(f"Error sending verification email to {user.email}: {e}")
        send_ok = False

    # 6️⃣ Final response: always return success for registration, but indicate email send result
    if send_ok:
        return {"message": "OTP sent to your email. Please verify to continue"}
    else:
        logger.warning(f"Verification OTP NOT sent to {user.email}")
        return {
            "message": "Account created. Verification email could not be sent — please contact support or retry later",
            "email_sent": False
        }

class VerifyEmailRequest(BaseModel):
    otp: str

@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest):

    # 1️⃣ Find valid OTP
    token_doc = await db["email_verification_tokens"].find_one({
        "otp": request.otp,
        "used": False,
        "expires_at": {"$gt": datetime.utcnow()}
    })

    if not token_doc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    # 2️⃣ Mark user as email_verified = True
    await db["users"].update_one(
        {"_id": ObjectId(token_doc["user_id"])},
        {"$set": {"email_verified": True}}
    )

    # 3️⃣ Mark OTP as used
    await db["email_verification_tokens"].update_one(
        {"_id": token_doc["_id"]},
        {"$set": {"used": True}}
    )

    return {
        "message": "Email verified successfully. Please login."
    }

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )

    # 🔐 NEW CHECK (VERY IMPORTANT)
    if "email_verified" in user and not user["email_verified"]:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before login"
        )

    access_token = create_access_token(str(user["_id"]))
    return Token(access_token=access_token)


# # -------------------- REGISTER --------------------
# @router.post("/register", response_model=UserOut)
# async def register(user: UserCreate):
#     # Check if user exists
#     existing_user = await get_user_by_email(user.email)
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User already exists")

#     # Create user document
#     user_dict = {
#         "email": user.email,
#         "password_hash": hash_password(user.password),  # Store hash, not raw password
#         "role": user.role,
#         "created_at": datetime.utcnow()
#     }

#     # Insert into database
#     result = await db["users"].insert_one(user_dict)

#     # Return user info
#     return UserOut(
#         id=str(result.inserted_id),
#         email=user.email,
#         role=user.role
#     )


# @router.post("/login", response_model=Token)
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = await authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
    
#     access_token = create_access_token(str(user["_id"]))
#     return Token(access_token=access_token)

# -------------------- PROTECTED ROUTE --------------------
@router.get("/protected")
async def protected_route(user: dict = Depends(require_role("admin"))):
    return {"message": "You have access to this admin route"}


# -------------------- PASSWORD RESET ENDPOINTS --------------------

# Request model for password reset
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# @router.post("/forgot-password")
# async def forgot_password(email: str):
#     """
#     Generate a password reset token and (in production) email it to the user.
#     """
#     user = await get_user_by_email(email)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Create a short-lived reset token (valid for 15 minutes)
#     reset_token = create_access_token(str(user["_id"]), expires_delta=timedelta(minutes=15))

#     # TODO: Send reset_token via email (here we just return it for testing)
#     return {
#         "message": "Password reset token generated successfully",
#         "reset_token": reset_token
#     }


# @router.get("/verify-reset-token/{token}")
# async def verify_reset_token(token: str):
#     """
#     Verify if a reset token is valid or expired.
#     """
#     try:
#         payload = decode_access_token(token)
#         return {"valid": True, "user_id": payload["sub"]}
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid or expired token")

# @router.post("/reset-password")
# async def reset_password(data: ResetPasswordRequest):
#     """Reset the user's password using a valid reset token."""
#     try:
#         # Decode and validate token using your existing helper
#         payload = decode_access_token(data.token)
#         user_id = payload.get("sub")
#         if not user_id:
#             raise HTTPException(status_code=400, detail="Invalid token payload")
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid or expired token")

#     # Validate and convert user_id
#     try:
#         object_id = ObjectId(user_id)
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid user ID format")

#     # Hash the new password securely
#     new_hashed = hash_password(data.new_password)

#     # Update password in MongoDB
#     result = await db["users"].update_one(
#         {"_id": object_id},
#         {"$set": {"password_hash": new_hashed}}
#     )

#     if result.modified_count == 0:
#         raise HTTPException(status_code=400, detail="Password reset failed")

#     return {"message": "Password has been reset successfully"}



#added apis 
# Add these models near your existing models
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Password reset token storage (in production, use Redis/database)
password_reset_tokens = {}
# In app/routes/auth.py - Update the forgot_password function

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email"""
    logger.info(f"Forgot password request for: {request.email}")
    
    # Find user
    user = await find_user_by_email(request.email)
    if not user:
        # For security, don't reveal if email exists
        logger.info(f"No user found with email: {request.email} (but returning success)")
        return {"message": "If an account exists, a reset link has been sent"}
    
    logger.info(f"✅ User found: {user.get('email')}")
    
    # Debug: Print user structure
    logger.debug(f"User keys: {list(user.keys())}")
    logger.debug(f"User _id: {user.get('_id')}")
    
    # Get user ID - handle both "_id" and "id"
    user_id = None
    if "_id" in user:
        user_id = str(user["_id"])
    elif "id" in user:
        user_id = str(user["id"])
    
    if not user_id:
        logger.error(f"❌ User has no ID field: {user}")
        raise HTTPException(
            status_code=500,
            detail="User data error"
        )
    
    # Create a numeric OTP (6 digits)
    import random
    reset_token = f"{random.randint(0, 999999):06d}"
    logger.info(f"Created OTP reset token for user ID: {user_id}")

    # Store token in database with 10-minute expiry
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    token_stored = await store_password_reset_token(reset_token, user_id, expires_at)
    
    if not token_stored:
        logger.error("Failed to store password reset token in database")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    
    # Send email
    try:
        # Send OTP email
        success = await email_service.send_password_reset_otp(
            to_email=request.email,
            otp=reset_token,
            user_name=user.get("email", "").split("@")[0],
            expiry_minutes=10
        )
        
        if success:
            logger.info(f"✅ Password reset email sent to {request.email}")
            return {"message": "Password reset email sent"}
        else:
            logger.error(f"❌ Failed to send email to {request.email}")
            # Still return success to user, but log the error
            return {"message": "If an account exists, a reset link has been sent"}
            
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        # Still return success to user for security
        return {"message": "If an account exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using token"""
    logger.info("Password reset request received")
    
    # Validate token
    user = await validate_password_reset_token(request.token)
    if not user:
        logger.warning("Invalid or expired password reset token")
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )
    
    # Update password
    hashed_password = hash_password(request.new_password)
    success = await update_user_password(str(user["id"]), hashed_password)
    
    if not success:
        logger.error(f"Failed to update password for user: {user['email']}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update password"
        )
    
    # Mark token as used
    await mark_password_reset_token_used(request.token)
    
    logger.info(f"✅ Password reset successful for user: {user['email']}")
    return {"message": "Password reset successful"}

@router.post("/logout")
async def logout():
    """
    Simple logout endpoint.
    Client should remove the token from localStorage/sessionStorage.
    """
    return {"message": "Successfully logged out"}


