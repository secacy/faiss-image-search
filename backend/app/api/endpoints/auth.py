"""
认证API端点
简单的认证功能，主要用于管理员登录
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str = None
    user_info: dict = None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """管理员登录"""
    # 简单的硬编码认证（实际项目中应该使用数据库和密码哈希）
    if request.username == "admin" and request.password == "admin123":
        return LoginResponse(
            success=True,
            message="登录成功",
            token="fake-jwt-token",  # 实际项目中应该生成真实的JWT
            user_info={
                "username": "admin",
                "role": "admin"
            }
        )
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")


@router.post("/logout")
async def logout():
    """登出"""
    return {"success": True, "message": "登出成功"}


@router.get("/me")
async def get_current_user():
    """获取当前用户信息"""
    # 简化实现，实际项目中应该验证JWT token
    return {
        "success": True,
        "data": {
            "username": "admin",
            "role": "admin"
        }
    } 