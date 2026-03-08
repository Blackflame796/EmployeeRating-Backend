# Схемы Pydantic для валидации данных сотрудников
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

class EmployeeSchema(BaseModel):
    """Базовая схема данных сотрудника для создания/обновления"""
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    second_name: str
    surname: str
    
    # Основные показатели эффективности (KPI)
    revenue: float = Field(ge=0, description="Выручка сотрудника (рубли)")
    quality: int = Field(ge=0, description="Количество закрытых задач")
    discipline: int = Field(ge=0, description="Количество опозданий")
    experience_years: float = Field(ge=0, default=0, description="Опыт работы (годы)")
    projects_completed: int = Field(ge=0, default=0, description="Выполненных проектов")
    client_satisfaction: float = Field(ge=0, le=5, default=4.0, description="Удовлетворённость клиентов (1-5)")
    teamwork_score: float = Field(ge=1, le=5, default=4.0, description="Оценка командной работы (1-5)")
    
    salary: Optional[float] = Field(ge=0, default=0, description="Заработная плата (рубли)")
    department_id: int
    
    # Весовые коэффициенты для расчета рейтинга
    weight_revenue: float = 0.5
    weight_quality: float = 0.3
    weight_discipline: float = 0.2

    rating: float = 0.0

class EmployeeCreate(EmployeeSchema):
    """Схема для создания нового сотрудника"""
    pass

class EmployeeRead(BaseModel):
    """Схема для чтения данных сотрудника (возвращается клиенту)"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    second_name: Optional[str] = None
    department_id: Optional[int] = None
    surname: str
    
    # Метрики
    revenue: float = 0.0
    quality: int = 0
    discipline: int = 0
    experience_years: Optional[float] = 0.0
    projects_completed: Optional[int] = 0
    client_satisfaction: Optional[float] = 4.0
    teamwork_score: Optional[float] = 4.0
    
    salary: Optional[float] = 0.0
    rating: float = 0.0

class RankingResponse(BaseModel):
    """Схема ответа со списком сотрудников и рассчитанными рейтингами"""
    employees: List[EmployeeRead]

    @model_validator(mode='after')
    def calculate_rankings(self) -> 'RankingResponse':
        """Валидатор-процедура для автоматического расчета рейтинга каждого сотрудника"""
        if not self.employees: return self
        
        # Сбор всех значений для нормализации
        revs = [e.revenue for e in self.employees]
        quals = [e.quality for e in self.employees]
        discs = [e.discipline for e in self.employees]

        def to_score(val, all_values, reverse=False):
            """Функция нормализации значения в балл от 0 до 10"""
            filtered_values = [v for v in all_values if v is not None]
            if not filtered_values:
                return 0.0
            v_min, v_max = min(filtered_values), max(filtered_values)
            if v_max == v_min: return 10.0
            if val is None:
                val = 0.0
            score = ((val - v_min) / (v_max - v_min)) * 10
            return 10 - score if reverse else score

        # Применение формулы расчета для каждого сотрудника
        for emp in self.employees:
            # Выручка: больше => лучше
            r_score = to_score(emp.revenue, revs)
            # Заявки: больше => лучше
            q_score = to_score(emp.quality, quals)
            # Опоздания: меньше опозданий => лучше балл (reverse=True)
            d_score = to_score(emp.discipline, discs, reverse=True)
            # Опыт: больше опыта => лучше балл
            exp_score = to_score(emp.experience_years, [e.experience_years for e in self.employees])
            # Выполненные проекты: больше проектов => лучше балл
            proj_score = to_score(emp.projects_completed, [e.projects_completed for e in self.employees])
            # Удовлетворённость клиентов: больше удовлетворённости => лучше балл
            client_satisfaction_score = to_score(emp.client_satisfaction, [e.client_satisfaction for e in self.employees])
            # Командная работа: больше оценки => лучше балл
            team_score = to_score(emp.teamwork_score, [e.teamwork_score for e in self.employees])

            # Итоговый расчет рейтинга с учетом весов
            emp.rating = round((r_score * 0.2) + (q_score * 0.2) + (d_score * 0.1) + (exp_score * 0.15) + (proj_score * 0.15) + (client_satisfaction_score * 0.1) + (team_score * 0.05), 2)
            
        return self