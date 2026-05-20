from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.schemas import user as user_schema
from app.schemas import captcha as captcha_schema
from app.models.user import User
from app.models.captcha import Captcha
from app.models.user_otp import UserOTP
from captcha.image import ImageCaptcha
import random
import uuid
import base64
import io

router = APIRouter()

@router.get("/captcha", response_model=captcha_schema.Captcha)
async def get_captcha(
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    # Generate traditional image captcha
    characters = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ" # Avoid ambiguous chars like 0, O, 1, l
    answer = "".join(random.choices(characters, k=5))
    
    generator = ImageCaptcha(width=200, height=80)
    image_data = generator.generate(answer)
    base64_image = base64.b64encode(image_data.getvalue()).decode()
    challenge = f"data:image/png;base64,{base64_image}"
    
    db_obj = Captcha(challenge=challenge, answer=answer)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.post("/login/access-token", response_model=user_schema.Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    captcha_id: uuid.UUID = Form(...),
    captcha_answer: str = Form(...)
) -> Any:
    # Verify captcha
    result = await db.execute(select(Captcha).filter(Captcha.id == captcha_id))
    captcha = result.scalars().first()
    
    if not captcha:
        raise HTTPException(status_code=400, detail="Invalid captcha session")
    
    if captcha.answer.lower() != captcha_answer.strip().lower():
        # Delete failed captcha
        await db.delete(captcha)
        await db.commit()
        raise HTTPException(status_code=400, detail="Incorrect captcha answer")
    
    # Delete successful captcha (use once)
    await db.delete(captcha)
    await db.commit()

    user = await crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=user_schema.User)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: user_schema.UserCreate
) -> Any:
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    # Create user but unverified
    user = await crud_user.create(db, obj_in=user_in)
    
    # Generate OTP
    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Delete any existing OTP for this email
    result = await db.execute(select(UserOTP).filter(UserOTP.email == user_in.email))
    existing_otps = result.scalars().all()
    for existing in existing_otps:
        await db.delete(existing)
        
    otp_obj = UserOTP(email=user_in.email, code=otp_code, expires_at=expires_at)
    db.add(otp_obj)
    await db.commit()
    
    # In a real app, send mail here. We'll simulate it by printing to console.
    print(f"\n[DRIVE X SECURITY] OTP for {user_in.email}: {otp_code}\n")
    
    return user

@router.post("/verify-otp", response_model=user_schema.User)
async def verify_otp(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_in: user_schema.OTPVerify
) -> Any:
    result = await db.execute(select(UserOTP).filter(UserOTP.email == verify_in.email))
    otp = result.scalars().first()
    
    if not otp:
        raise HTTPException(status_code=400, detail="Verification code not found or expired")
        
    if otp.is_expired():
        await db.delete(otp)
        await db.commit()
        raise HTTPException(status_code=400, detail="Verification code expired")
        
    if otp.code != verify_in.code:
        raise HTTPException(status_code=400, detail="Incorrect verification code")
        
    # Mark user as verified
    user = await crud_user.get_by_email(db, email=verify_in.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_verified = True
    db.add(user)
    
    # Cleanup OTP
    await db.delete(otp)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/me", response_model=user_schema.User)
async def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    return current_user

@router.post("/change-password")
async def change_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    password_in: user_schema.PasswordChange,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    if not security.verify_password(password_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    current_user.hashed_password = security.get_password_hash(password_in.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password updated successfully"}
