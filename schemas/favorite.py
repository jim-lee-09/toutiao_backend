from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorited: bool=Field(...,alias="isFavorite")

# 添加收藏：
class FavoriteAddRequest(BaseModel):
    news_id: int=Field(...,alias="newsId")

#列表里面的数据类型
# 这里规划两个类：一个是新闻模型类+收藏的模型类
# 新闻模型类在schemas的base文件中

# 下面就是收藏模型类
class FavoriteNewsItemsResponse(NewsItemBase):
    favorite_id: int=Field(...,alias="favoriteId")
    favorite_time: datetime=Field(...,alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

# 获取收藏列表-响应模型类
class FavoriteListResponse(BaseModel):
    list:list[FavoriteNewsItemsResponse]
    total:int
    has_more: bool=Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
