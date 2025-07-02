from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any, List

from app.models.user import User, UserCreate, UserUpdate, UserInDB
from app.services.user import UserService
from app.core.security import create_access_token
from app.api.deps import get_current_user, get_user_service

router = APIRouter()

@router.post("/register", response_model=User)
async def register(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    注册新用户。
    """
    user = await user_service.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )
    user = await user_service.create(user_in=user_in)
    return user

@router.post("/login", response_model=dict)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    用户登录，获取访问令牌。
    """
    user = await user_service.authenticate(
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }

@router.get("/profile", response_model=User)
async def get_user_profile(
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    获取当前登录用户的信息。
    """
    return current_user

@router.put("/profile", response_model=User)
async def update_user_profile(
    user_in: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    更新当前用户信息。
    """
    user = await user_service.update(user_id=current_user.id, user_in=user_in)
    return user

@router.post("/risk-assessment", response_model=dict)
async def assess_health_risk(
    data: dict,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    进行健康风险评估。
    """
    # 这里将调用风险评估服务
    risk_score = await user_service.assess_risk(user_id=current_user.id, data=data)
    return {
        "risk_score": risk_score,
        "risk_level": "低风险" if risk_score < 30 else "中风险" if risk_score < 60 else "高风险",
        "recommendations": [
            "定期监测血糖",
            "保持健康饮食",
            "适量运动"
        ]
    } 