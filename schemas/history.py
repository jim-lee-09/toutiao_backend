from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    news_id: int=Field(...,alias="newsId")


# 获取浏览列表响应数据类型
class HistoryListResponse(BaseModel):
    list:list[HistoryNewsItemsResponse]
    total:int
    has_more:bool=Field(...,alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

# 获取浏览列表响应数据类型中列表的类型
class HistoryNewsItemsResponse(NewsItemBase):
    history_id:int=Field(...,alias="historyId")
    view_time:datetime=Field(...,alias="viewTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )