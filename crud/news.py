from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func,update
from models.news import Category, News


#新闻分类函数-获取八个新闻分类
async def get_categories(db:AsyncSession,skip:int=0,limit:int=100):
    stmt=select(Category).offset(skip).limit(limit)
    result=await db.execute(stmt)
    return result.scalars().all()

#查询新闻列表
async def get_news_list(db:AsyncSession,category_id:int,skip:int=0,limit:int=10):
    #查询的是指定分类下的所有新闻
    stmt=select(News).where(News.category_id==category_id).offset(skip).limit(limit) # 输入八个分类任意id 找新闻表中哪些数据存有参数输入的id
    result=await db.execute(stmt)
    return result.scalars().all()

#计算总量
async def get_news_count(db:AsyncSession,category_id:int):
    # 查询的是指定分类下的所有新闻
    stmt=select(func.count()).where(News.category_id==category_id)
    result=await db.execute(stmt)
    return result.scalar_one() # 只能有一个结果，否则报错

#查询新闻的详细信息
async def get_news_detail(db:AsyncSession,news_id:int):
    stmt=select(News).where(News.id==news_id)
    result=await db.execute(stmt)
    return result.scalar_one_or_none() # 返回的是数据库的一行数据或者返回None

#在查询到询问详细信息的基础上增加浏览量
async def increase_news_views(db:AsyncSession,news_id:int):
    stmt=update(News).where(News.id==news_id).values(views=News.views + 1)
    result=await db.execute(stmt)
    await db.commit()
    #更新->检查数据库是否真的命中了数据->命中了返回True
    return result.rowcount>0 # row就是行 count就是数量 这里rowcount=1

# 推荐相关类型的新闻
async def get_related_news(db:AsyncSession,news_id:int,category_id:int,limit:int=5):
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
    return [{
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

