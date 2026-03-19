# Модуль для работы с базой данных SQLAlchemy
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings

# Формирование строк подключения из настроек
connect_link = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Настройка асинхронного движка SQLAlchemy
# NullPool используется для избежания проблем с пулом соединений в асинхронной среде
engine = create_async_engine(
    connect_link,
    echo=False,
    poolclass=NullPool,
)

# Создание фабрики сессий
session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Зависимость (Dependency) для внедрения сессии БД в эндпоинты FastAPI
async def get_session() -> AsyncSession:
    """Асинхронный генератор сессий для работы с БД"""
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

# Функция корректного закрытия движка при завершении приложения
async def dispose_engine():
    """Освобождение всех ресурсов движка БД"""
    await engine.dispose()