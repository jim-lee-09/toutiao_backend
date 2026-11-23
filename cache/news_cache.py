#新闻相关的缓存方法：新闻分类的读取和写入
#缓存的格式是key-value，所以先手动设置key
from config.cache_conf import get_json_cache, set_cache
from typing import List, Dict, Any, Optional

CATEGORIES_KEY="news:categories" #为什么这样写key
NEWS_LIST_PREFIX="news_list:"
NEWS_DETAIL_PREFIX="news:detail:"
RELATED_NEWS_PREFIX = "news:related:"

#获取(读取)新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY) #为什么返回这个解码器(读取函数)


#写入新闻分类缓存：缓存的数据，过期时间
#分类、配置 7200；列表：600；详情：1800；验证码：120---数据越稳定，缓存越持久
#避免所有key同时过期 引起缓存雪崩
async def set_cache_categories(data:List[Dict[str,Any]],expire:int=7200):  #为什么data数据类型长这样 怎么理解
    return await set_cache(CATEGORIES_KEY,data,expire)


#写入缓存-新闻列表
#参数的选择->从key的格式去找 key:news_list:分类id:页码：每页数量  +列表数据 +过期时间
async def set_cache_news_list(category_id:Optional[int],page:int,size:int,news_list:List[Dict[str,Any]],expire:int=600):
    #调用 封装的Redis的设置方法，存新闻列表到缓存
    category_part=category_id if category_id is not None else "all"
    key=f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await set_cache(key,news_list,expire)

"""这个写入缓存的封装函数"""
#参数category_id解释一下为什么是这个类型 为什么有的新闻可以没有类型
#if这句语法好久没见了
#key的构成使用了拼接方式 更灵活---目的是不是方便把新闻列表的每一条数据都覆盖上并写入缓存？

#读取缓存-新闻列表
async def get_cache_news_list(category_id:Optional[int],page:int,size:int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)


#写入缓存-新闻详情
#封装写入读取缓存的参数设计->key=news:detail:{news_id}
async def cache_news_detail(news_id:int,news_data:Dict[str,Any],expire:int=300):
    key=f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await set_cache(key,news_data,expire)

#读取缓存-新闻详情
async def get_cached_news_detail(news_id:int):
    key=f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await get_json_cache(key)

#写入缓存-推荐相关新闻
#key设计 key=news:related:{news_id}:{category_id}
async def cache_related_news(news_id:int,category_id:int,data:List[Dict[str,Any]],expire:int=1800):
    key=f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await set_cache(key,data,expire)

#读取缓存-推荐相关新闻
#key设计
async def get_cached_related_news(news_id:int,category_id:int):
    key=f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await get_json_cache(key)
