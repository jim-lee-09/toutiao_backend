"""这个包的作用就是缓存的crud函数，实质是在news-crud的基础上进行修改"""
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func,update

from cache.news_cache import get_cached_categories, set_cache_categories, get_cache_news_list, set_cache_news_list, \
    cache_news_detail, get_cached_news_detail, get_cached_related_news, cache_related_news
from models.news import Category, News
from schemas.base import NewsItemBase


#新闻分类函数-获取八个新闻分类
async def get_categories(db:AsyncSession,skip:int=0,limit:int=100):
    # 先尝试从缓存中读取数据
    cached_categories=await get_cached_categories()
    if cached_categories:
        return cached_categories
    #缓存中没有数据，就检索数据库
    stmt=select(Category).offset(skip).limit(limit)
    result=await db.execute(stmt)
    categories = result.scalars().all() #查完数据库之后不直接返回，先写入缓存再返回数据

    # 写入缓存
    if categories:
        #因为查完数据库返回的数据是ORM类型：categories是ORM类型
        #写入缓存需要是列表 字典这种字符串，因此需要转类型
        categories=jsonable_encoder(categories) #这个语法可以实现从ORM等复杂类型转换成简单类型
        await set_cache_categories(categories)
    #返回数据
    return categories

"""针对上面旁路策略的一些疑惑"""
#写入缓存这一部分:我知道写入缓存需要传入字符串 但是这里这种情况是ORM转字符串吗 还是转python类型 比如list dict
#categories=jsonable_encoder(categories)  这个语法还能把什么复杂类型转成简单类型
#最后就是写入缓存封装的方法set_cache_categories(categories) 参数类型是什么意思


#查询新闻列表
async def get_news_list(db:AsyncSession,category_id:int,skip:int=0,limit:int=10):
    #读取缓存-先尝试从缓存中获取新闻列表
    #注意该crud函数中没有页码函数-需要自己计算
    #跳过的数量=（页码-1）*pagesize->页码=跳过的数量//pagesize+1
    page=skip//limit+1
    cached_list=await get_cache_news_list(category_id,page,limit) #缓存中是json格式
    if cached_list:
        # return cache_list 不能直接return 因为要的是ORM对象 要的应该是python对象类型才对啊
        return [News(**item) for item in cached_list]

    #查询的是指定分类下的所有新闻
    stmt=select(News).where(News.category_id==category_id).offset(skip).limit(limit) # 输入八个分类任意id 找新闻表中哪些数据存有参数输入的id
    result=await db.execute(stmt)
    news_list=result.scalars().all()

    #写入缓存
    if news_list:
        # news_list=jsonable_encoder(news_list)
        # 先把ORM数据转换成pydantic格式，再转为字典
        #by_alias=False不适用别名，保存python风格，因为Redis数据是给后端用的
        news_data=[NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in news_list]
        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list


#计算总量
async def get_news_count(db:AsyncSession,category_id:int):
    # 查询的是指定分类下的所有新闻
    stmt=select(func.count()).where(News.category_id==category_id)
    result=await db.execute(stmt)
    return result.scalar_one() # 只能有一个结果，否则报错

#查询新闻的详细信息 -需要加入缓存
async def get_news_detail(db:AsyncSession,news_id:int):

    #读取缓存
    cache_news=await get_cached_news_detail(news_id)
    if cache_news:
        return News(**cache_news)# 因为新闻详情数据的格式是{....}所以说直接解包就行了


    stmt=select(News).where(News.id==news_id)
    result=await db.execute(stmt)
    news=result.scalar_one_or_none() # 返回的是数据库的一行数据或者返回None

    #写入缓存
    if news:
        #ORM对象先转成python对象再由底层函数处理成JSON格式  这里为什么不需要转换成pydantic类型啊
        result=jsonable_encoder(news)
        await cache_news_detail(news_id,result)
    return news


#在查询到询问详细信息的基础上增加浏览量
async def increase_news_views(db:AsyncSession,news_id:int):
    stmt=update(News).where(News.id==news_id).values(views=News.views + 1)
    result=await db.execute(stmt)
    await db.commit()
    #更新->检查数据库是否真的命中了数据->命中了返回True
    return result.rowcount>0 # row就是行 count就是数量 这里rowcount=1

# 推荐相关类型的新闻-- 加入缓存
async def get_related_news(db:AsyncSession,news_id:int,category_id:int,limit:int=5):

    #读取缓存
    cached_related=await get_cached_related_news(news_id,category_id)
    if cached_related:
        return cached_related

    #order_by排序->浏览量和发布时间
    stmt=select(News).where(
        News.category_id==category_id,
        News.id!=news_id
    ).order_by(
        News.views.desc(),# order_by默认升序，desc()降序
        News.publish_time.desc()
    ).limit(limit)
    result=await db.execute(stmt)
    # return result.scalars().all()
    related_news=result.scalars().all()
    #列表推导式 推导出新闻的核心数据，然后再return 返回的格式是字典格式
    related_list= [{
        "id": news_detail.id,
        "title": news_detail.title,
        "description": news_detail.description,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views
    } for news_detail in related_news]

    #写入缓存
    if related_list:
        await cache_related_news(news_id,category_id,jsonable_encoder(related_list))
    return related_list