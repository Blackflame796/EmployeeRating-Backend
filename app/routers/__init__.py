from .employee import router as employee_router
from .department import router as department_router

__all__ = [
    "employee_router",
    "department_router"
]