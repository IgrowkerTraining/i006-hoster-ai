from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config.settings import settings

main_engine = create_async_engine(
    settings.MAIN_DATABASE_URL
    )

ai_engine = create_async_engine(
    settings.AI_DATABASE_URL,
    echo=False
)

MainSessionLocal = async_sessionmaker(
    main_engine, 
    expire_on_commit=False
)

AIAsyncSessionLocal = async_sessionmaker(
    ai_engine,
    expire_on_commit=False
)