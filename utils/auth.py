# auth就是认证的文件->封装认证工具函数
from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users


#整合 根据Token 查询用户，返回用户 ->鉴权函数
async def get_current_user(authorization: str = Header(...,name="Authorization"),
    db:AsyncSession=Depends(get_db)
):
    #前端请求头格式 Bearer xxxxxx
    #token=authorization.split(" ")[1] # 获取token的第一种写法
    token=authorization.replace("Bearer ","")#把Bearer换成空格，直接得到token
    user=await users.get_user_by_token(db,token) #调用查Token和查询功能模块
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="无效的令牌或者已经过期的令牌")
    return user



    #不能直接调用函数传入authorization 因为前端有请求头的格式
    # users.get_user_by_token(db,authorization)

