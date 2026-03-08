# Точка входа в приложение FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Импорт роутеров для сотрудников и отделов
from app.routers import employee_router, department_router

# Инициализация приложения
app = FastAPI(title="Система рейтинга сотрудников API")

# Настройка CORS для взаимодействия с фронтендом
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(employee_router)
app.include_router(department_router)

# Запуск сервера разработки
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
