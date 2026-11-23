# 添加浏览记录
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from models.history import History
from models.news import News


async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int,
):
    # 先检查是否有这条新闻
    # 我的思路：查history表是否有该新闻->有更新浏览时间 无就添加浏览历史
    query=select(History).where(History.user_id == user_id, History.news_id == news_id)
    result=await db.execute(query)
    existing_history=result.scalar_one_or_none()
    if existing_history:
        existing_history.view_time=datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history=History(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

#获取收藏列表
async def get_history(
        db: AsyncSession,
        user_id: int,
        page: int ,
        page_size: int
):
    #先计算总量
    count_query=select(func.count()).where(History.user_id == user_id)
    count_result=await db.execute(count_query)
    total=count_result.scalar_one_or_none()

    offset=(page-1)*page_size
    #再联表查询 News+History
    query=(select(News,History.view_time,History.id.label("history_id"))
     .join(History,History.news_id==News.id)
     .where(History.user_id == user_id)
    .order_by(History.view_time.desc())
     .offset(offset)
     .limit(page_size)
     )
    result=await db.execute(query)
    #注意要打包rows
    rows=result.all()
    return rows,total


#删除单条浏览数据
async def remove_history(
        db: AsyncSession,
        user_id: int,
        news_id:int
):
    query=delete(History).where(History.user_id == user_id,History.news_id == news_id)
    stmt=await db.execute(query)
    await db.commit()
    return stmt.rowcount>0

# 清空浏览记录
async def clear_history(
        db: AsyncSession,
        user_id: int
):
    delete_query=delete(History).where(History.user_id == user_id)
    stmt=await db.execute(delete_query)
    await db.commit()
    return stmt.rowcount or 0
