# Роутер для управления сотрудниками
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.employee import EmployeeModel
from app.schemas.employee import EmployeeRead, EmployeeCreate, RankingResponse

router = APIRouter(prefix="/employees", tags=['Работа с сотрудниками'])

@router.post("/create", response_model=EmployeeRead)
async def create_employee(employee: EmployeeCreate, session: AsyncSession = Depends(get_session)):
    """Создать нового сотрудника в базе данных"""
    data = employee.model_dump(exclude={
        "weight_revenue", 
        "weight_quality", 
        "weight_discipline", 
        "rating"
    })
    new_employee = EmployeeModel(**data)
    session.add(new_employee)
    await session.commit()
    await session.refresh(new_employee)
    return new_employee

@router.get("/all", response_model=List[EmployeeRead])
async def get_all_employees(session: AsyncSession = Depends(get_session)):
    """Получить список всех сотрудников без рейтинга"""
    data = await session.scalars(select(EmployeeModel))
    return data.all()

@router.get("/rating", response_model=RankingResponse)
async def get_ranking(
    limit: Optional[int] = Query(None, ge=1, le=100, description="Количество сотрудников"),
    sort_by: Optional[Literal['revenue', 'quality', 'discipline']] = Query(None, description="Поле для сортировки"),
    order: Literal['asc', 'desc'] = Query('desc', description="Направление (asc/desc)"),
    session: AsyncSession = Depends(get_session)
):
    """Рассчитать рейтинг и получить список сотрудников с учетом фильтров"""
    query = select(EmployeeModel)
    
    result = await session.execute(query)
    employees = result.scalars().all()
    
    ranking_response = RankingResponse(employees=list(employees))

    # Сортировка по базовым полям (не по рассчитанному рейтингу)
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

@router.get("/get/{employee_id}", response_model=EmployeeRead)
async def get_employee(employee_id: int, session: AsyncSession = Depends(get_session)):
    """Получить данные конкретного сотрудника по его ID"""
    employee = await session.get(EmployeeModel, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/update/{employee_id}", response_model=EmployeeRead)
async def update_employee(employee_id: int, updated_data: EmployeeCreate, session: AsyncSession = Depends(get_session)):
    """Обновить информацию о сотруднике"""
    employee = await session.get(EmployeeModel, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    data = updated_data.model_dump(exclude={
        "weight_revenue", 
        "weight_quality", 
        "weight_discipline", 
        "rating"
    })
    for key, value in data.items():
        setattr(employee,key,value)
    await session.commit()
    await session.refresh(employee)
    return employee

@router.delete("/delete/{employee_id}")
async def delete_employee(employee_id: int, session: AsyncSession = Depends(get_session)):
    """Удалить сотрудника из системы"""
    employee = await session.get(EmployeeModel, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    await session.delete(employee)
    await session.commit()
    return {"message": f"Employee with id={employee_id} was deleted successfully"}