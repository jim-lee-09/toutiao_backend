import json

import redis.asyncio as redis

REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0

redis_client=redis.Redis(
    host=REDIS_HOST,# Redis服务端在本机
    port=REDIS_PORT,# 服务端监听端口
    db=REDIS_DB,# 用第一个逻辑库(redis默认有0-15号库)
    decode_responses=True# 读出来的值是否自动解码成字符串
)

#设置 和 读取 (字符串，列表或字典) "[{}]"
#读取：字符串
async def get_cache(key:str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None


# 读取：；列表或字典
async def get_json_cache(key:str):
   try:
      data= await redis_client.get(key)
      if data:
          return json.loads(data) #反序列化：把JSON变成python对象
      return None
   except Exception as e:
       print(f"获取缓存失败：{e}")
       return None


# 设置缓存 setex(key,expire,value)
async def set_cache(key:str,value:str,expire:int=3600):
    try:
        if isinstance(value,(dict,list)): # 判断类型
            value = json.dumps(value,ensure_ascii=False) # 序列化 把python对象转换成JSON格式
        await redis_client.set(key, value, ex=expire)
        return True
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return False



