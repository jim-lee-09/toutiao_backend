from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from models.users import User, UserToken
from schemas.users import UserRequest,  UserUpdateRequest
from utils import security
import uuid
from sqlalchemy import update

from utils.security import verify_password


# 根据用户名查询数据库
async def get_user_by_username(db:AsyncSession, username:str):
    query=select(User).where(User.username == username)
    result=await db.execute(query)
    return result.scalar_one_or_none()


# 下面是使用Pydantic模型参数的写法
# async def get_user_by_username(db:AsyncSession, user_data:UserRequest):
#     query=select(User).where(User.username == user_data.username)
#     result=await db.execute(query)
#     return result.scalar_one_or_none()


# 封装创建用户
async def create_user(db:AsyncSession,user_data:UserRequest):
    # 先密码加密处理->add
    hashed_password=security.get_hash_password(user_data.password)
    user=User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user) #从数据库读回最新的user
    return user

# 生成Token->对应的Token模型类是UserToken
async def create_token(db:AsyncSession,user_id:int):
    # 生成Token+设置过期时间->查询数据库当前用户是否有Token->有：会更新；没有：添加
    token=str(uuid.uuid4())  #生成token->注意要转str格式
    expires_at=datetime.now()+timedelta(days=7) # 设置过期时间
    query=select(UserToken).where(UserToken.user_id == user_id) # 查找数据库当前用户是否有token
    result=await db.execute(query) # 链接数据库
    user_token=result.scalar_one_or_none() # 返回None或者一条数据

    if user_token: # 更新token和过期时间 这种更新token模式是单设备模式
        user_token.token=token
        user_token.expires_at=expires_at
    else:# 否则就创建一条新数据
        user_token=UserToken(user_id=user_id,token=token,expires_at=expires_at)
        db.add(user_token)
    await db.commit() # 提交到数据库中

    return token # 返回新token

# 用户登录模块-验证功能
async def authenticate_user(db:AsyncSession,username:str,password:str):  #这密码参数是明文
    #验证账号名
    user=await get_user_by_username(db,username)
    if not user:
        return None
    #验证密码
    if not security.verify_password(password, user.password): # 第一个参数是明文 后面是密文
        return None

    #数据库中有用户并且明文密文对应上了->返回该对象
    return user



# 根据 Token 查询用户：验证Token -> 查询用户
async def get_user_by_token(db:AsyncSession,token:str):
    query=select(UserToken).where(UserToken.token == token)
    # 下面这行代码的作用是什么 上面的代码不是已经知道是否找到了吗
    result=await db.execute(query)
    db_token=result.scalar_one_or_none()

    if not db_token or db_token.expires_at<datetime.now():
        return None

    query=select(User).where(User.id == db_token.user_id)
    result=await db.execute(query)
    return result.scalar_one_or_none()

# 更新用户信息->为什么参数并不用user_id而是使用username
async def update_user(db:AsyncSession,username:str,user_data:UserUpdateRequest):
    # update(User).where(User.username==username).values(键=值，键=值)
    # 因为user_data是pydantic类型，不是键=值的格式，所以先打包成字典再解包
    # 因为更新模型类默认值为None 实际情况是没有更改需求的情况下默认原内容不变 只有修改的内容会变->给model_dump加参数
    query=update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_none=True,
        exclude_unset=True
    ))
    result=await db.execute(query)  # 这一行到底会返回什么 为什么后面验证命中会用到该变量
    await db.commit()

    # 验证更新命中->写的时候没有注意验证命中
    if result.rowcount==0:
        raise HTTPException(status_code=404,detail="用户不存在")

    #更新完之后查找对应用户的信息
    update_user=await get_user_by_username(db,username)
    return update_user

#修改密码：验证旧密码->新密码加密->修改密码
async def change_password(db:AsyncSession,user:User,old_password:str,new_password:str):
    if not security.verify_password(old_password,user.password):
        return False

    hashed_pwd=security.get_hash_password(new_password)
    user.password=hashed_pwd
    # 更新：由SQLAchemy真正接管这个User对象，确保可以commit
    # 规避session 过期或关闭导致的不能提交的问题
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True















