from passlib.context import CryptContext

# 创建密码上下文
psw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 密码加密
def get_hash_password(password:str):
    return psw_context.hash(password)

# 密码验证: verify返回值是布尔型
def verify_password(plain_password:str,hashed_password:str):
    return psw_context.verify(plain_password, hashed_password)
