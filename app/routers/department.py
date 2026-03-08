# Роутер для управления отделами
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.department import DepartmentModel
from app.models.employee import EmployeeModel
from app.schemas.department import DepartmentSchema, DepartmentResponse
from app.schemas.employee import RankingResponse

router = APIRouter(prefix="/departments")

@router.post("/create", response_model=DepartmentResponse)
async def create_department(department: DepartmentSchema, session: AsyncSession = Depends(get_session)):
    """Создать новый отдел в системе"""
    data = department.model_dump()
    new_department = DepartmentModel(**data)
    session.add(new_department)
    await session.commit()
    await session.refresh(new_department)
    return new_department

@router.get("/get/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: int, session: AsyncSession = Depends(get_session)):
    """Получить данные отдела по его ID"""
    department = await session.get(DepartmentModel, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.put("/update/{department_id}", response_model=DepartmentResponse)
async def update_department(department_id: int, updated_data: DepartmentSchema, session: AsyncSession = Depends(get_session)):
    """Обновить название или другие данные отдела"""
    department = await session.get(DepartmentModel, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    data = updated_data.model_dump()
    for key, value in data.items():
        setattr(department, key, value)
    await session.commit()
    await session.refresh(department)
    return department

@router.delete("/delete/{department_id}")
async def delete_department(department_id: int, session: AsyncSession = Depends(get_session)):
    """Удалить отдел из системы"""
    department = await session.get(DepartmentModel, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    await session.delete(department)
    await session.commit()
    return {"message": f"Department with id={department_id} was deleted"}

@router.get("/all", response_model=List[DepartmentResponse])
async def get_all_departments(session: AsyncSession = Depends(get_session)):
    """Получить список всех зарегистрированных отделов"""
    data = await session.scalars(select(DepartmentModel))
    return data.all()

@router.get("/get/{department_id}/rating", response_model=RankingResponse)
async def get_ranking(
    department_id: int,
    limit: Optional[int] = Query(None, ge=1, le=100, description="Количество сотрудников для отображения"),
    sort_by: Optional[Literal['revenue', 'quality', 'discipline']] = Query(None, description="Поле для сортировки"),
    order: Literal['asc', 'desc'] = Query('desc', description="Порядок сортировки"),
    session: AsyncSession = Depends(get_session)
):
    """Рассчитать рейтинг сотрудников конкретного отдела"""
    query = select(EmployeeModel).where(EmployeeModel.department_id == department_id)
    
    result = await session.scalars(query)
    employees = result.all()
    
    ranking_response = RankingResponse(employees=list(employees))

    # Логика сортировки по выбранному полю
    if sort_by != 'rating':
        reverse = (order == 'desc')
        
        if sort_by == 'revenue':
            ranking_response.employees.sort(key=lambda x: x.revenue, reverse=reverse)
        elif sort_by == 'quality':
            ranking_response.employees.sort(key=lambda x: x.quality, reverse=reverse)
        elif sort_by == 'discipline':
            ranking_response.employees.sort(key=lambda x: x.discipline, reverse=reverse)
    
    if limit is not None:
        ranking_response.employees = ranking_response.employees[:limit]
    return ranking_response