from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud.favorite import is_news_favorite, add_news_favorite, remove_news_favorite, remove_all_favorites
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response

from crud import favorite

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(
        news_id:int=Query(...,alias="newsId"),
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    is_favorited=await is_news_favorite(db,user.id,news_id)
    #注意不能直接把is_favorited直接传给data返回
    #为什么不能直接把is_favorited传给data
    return success_response(message="检查收藏状态成功",data=FavoriteCheckResponse(isFavorite=is_favorited))

# 添加收藏
@router.post("/add")
async def add_favorite(
        data:FavoriteAddRequest,
        db:AsyncSession=Depends(get_db),
        user:User=Depends(get_current_user)
):
    result=await add_news_favorite(db,user.id,data.news_id)
    return success_response(message="添加收藏成功",data=result)

# 取消收藏
@router.delete("/remove")
async def remove_favorite(
    news_id:int=Query(...,alias="newsId"),
    user:User=Depends(get_current_user),
    db:AsyncSession=Depends(get_db)
):
    result=await remove_news_favorite(db,user.id,news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="收藏记录不存在")
    return success_response(message="取消收藏成功")

# 获取收藏列表
@router.get("/list")
async def get_favorite_list(
        page:int=Query(1,ge=1),
        page_size:int=Query(10,ge=1,le=100,alias="pageSize"),
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    rows,total=await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list=[{
        **news.__dict__,
        "favorite_time":favorite_time,
        "favorite_id":favorite_id
    }for news,favorite_time,favorite_id in rows]
    has_more=total>page*page_size
    data=FavoriteListResponse(list=favorite_list,total=total,hasMore=has_more)
    return success_response(message="获取收藏列表成功",data=data)

# 清空收藏列表
@router.delete("/clear")
async def clear_favorite(
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    count=await remove_all_favorites(db,user.id)
    return success_response(message=f"清空了{count}条记录")










