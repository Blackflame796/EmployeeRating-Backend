# EmployeeRating-Backend

## Подготовка рабочего окружения

```bash
mkdir EmployeeRating
cd EmployeeRating
mkdir EmployeeRating-Backend EmployeeRating-Frontend
cd EmployeeRating-Backend
pip install uv --break-system-packages
uv init
uv add fastapi uvicorn sqlalchemy pydantic-settings python-dotenv alembic psycopg2-binary "celery[redis]" redis "sqlalchemy[asyncio]" asyncpg 
```
```

##  Активация рабочего окружения

```bash
source .venv/bin/activate # macOS, Linux
.venv\Scripts\activate # Windows
```



```bash
npm i react-router-dom --save styled-components
npm install clsx lucide recharts
```


https://recharts.github.io/en-US/examples/CustomContentOfTooltip/