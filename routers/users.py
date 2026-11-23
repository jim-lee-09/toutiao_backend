from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user
from starlette.status import HTTP_401_UNAUTHORIZED

from config.db_conf import get_db
from crud.users import change_password
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from crud import users
from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(
    prefix="/api/user",
    tags=["users"]
)
# 用户注册基础路由
@router.post("/register")
async def register(user_data:UserRequest,db:AsyncSession=Depends(get_db)):
    # 注册逻辑：检验用户是否存在->创建用户->生成Token->响应结果
    existing_user= await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")

    user=await users.create_user(db, user_data)

    token=await users.create_token(db, user.id)

    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user_data.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功",data=response_data)

# 登录模块
@router.post("/login")
async def login(user_data:UserRequest,db:AsyncSession=Depends(get_db)):
    # 登录逻辑：验证用户是否存在->验证密码->生成Token->相应结果
    user=await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="用户名或者密码错误")

    token=await users.create_token(db, user.id)
    response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))

    return success_response(message="登录成功啦",data=response_data)


# 获取用户信息
#1，我想问一下登录模块不是已经得到用户信息了吗：response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
#为啥还需要再获取信息啊
#2，为什么需要请求头
#3，为什么要使用依赖注入啊-路由导入使用：依赖注入
@router.get("/info")
async def get_user_info(user: User =Depends(get_current_user)):# 再给我讲一下这个依赖注入
    return success_response(message="获取个人信息成功",data=UserInfoResponse.model_validate(user))

# 修改用户信息
# 思路：接收前端数据->鉴权->抛出异常或者查找用户->找不到抛出异常-或者找到对应的用户信息->更改用户信息->响应结果
# @router.get("/update")->这个路由是post get还是put
# 思路(教程版本)：验证token-更新(用户输入数据put提交-请求体参数-定义Pydantic模型类)-响应结果

#参数：用户输入+验证token的+db(调用更新的方法)->为什么获取用户信息路由函数不需要额外设db依赖注入
#为什么更新模型类没有id name password
# 什么时候可以想获取用户信息一样使用依赖注入
# 鉴权函数在哪体现作用呢
@router.put("/update")
async def update_user_info(user_data:UserUpdateRequest,user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    user=await users.update_user(db,user.username,user_data)
    return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(user))


# 修改密码路由函数
@router.put("/password")
async def update_password(
        password_data:UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    res_change_pwd=await change_password(db,user,password_data.old_password,password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="修改密码失败，请稍后再试")

    return success_response(message="密码修改成功")
