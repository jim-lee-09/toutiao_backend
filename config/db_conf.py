#配置ORM
#先确定url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession,async_sessionmaker
SYSTEM_URL="mysql+aiomysql://root:123456@localhost:3306/news_app"
#写异步引擎
async_engine=create_async_engine(
    SYSTEM_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)
#写会话工厂
AsyncSessionLocal=async_sessionmaker(bind=async_engine,class_=AsyncSession,expire_on_commit=False)
#依赖项-准备后续的依赖注入-获取数据库会话
async def get_db():
    # async with async_engine.begin() as conn:
      async with AsyncSessionLocal() as session:
          try:
            yield session
            await session.commit()
          except Exception:
            await session.rollback()
            raise
          finally:
              await session.close()



