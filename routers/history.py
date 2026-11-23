
from fastapi import APIRouter, Depends,Query,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import history
from crud.history import get_history, remove_history
from models.news import News
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router= APIRouter(prefix="/api/history",tags=["history"])

@router.post("/add")
async def add_history(
        data:HistoryAddRequest,
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)

):
    result=await history.add_history(db,user.id,data.news_id)
    return success_response(message="添加浏览成功",data=result)

#获取浏览列表
@router.get("/list")
async def get_history_list(
        page:int = Query(1,ge=1),
        page_size:int =Query(10,ge=1,le=100,alias="pageSize"),
        db:AsyncSession=Depends(get_db),
        user:User=Depends(get_current_user)
):
    rows,total=await get_history(db,user.id,page,page_size)
    history_list=[{
        **news.__dict__,
        "view_time":view_time,
        "history_id":history_id
    }for news,view_time,history_id in rows]
    data=HistoryListResponse(list=history_list,total=total,hasMore=total>page*page_size)
    return success_response(message="获取浏览记录成功",data=data)

# 删除单条浏览数据
@router.delete("/delete/{news_id}")
async def delete_history(
        news_id:int,
        db:AsyncSession=Depends(get_db),
        user:User=Depends(get_current_user)
):
    result=await remove_history(db,user.id,news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message="删除成功")

@router.delete("/clear")
async def clear_history(
        uesr:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    data=await history.clear_history(db,uesr.id)
    return success_response(message="清空浏览记录成功")

