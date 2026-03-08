# Модель таблицы сотрудников
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from app.models.base import Base

class EmployeeModel(Base):
    """Описание структуры сотрудника в базе данных"""
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    second_name = Column(String, nullable=True)
    surname = Column(String, nullable=False)
    
    # Связь с отделом
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    department = relationship("DepartmentModel", back_populates="employees", lazy="selectin")
    
    # Метрики эффективности для расчета рейтинга
    revenue = Column(Float, default=0.0) # Выручка в рублях
    quality = Column(Integer, default=0) # Количество выполненных задач
    discipline = Column(Integer, default=0) # Количество опозданий
    experience_years = Column(Float, default=0.0) # Стаж работы
    projects_completed = Column(Integer, default=0) # Завершенные проекты
    client_satisfaction = Column(Float, default=4.0) # Отзывы клиентов
    teamwork_score = Column(Float, default=4.0) # Оценка командной работы
    
    salary = Column(Float, nullable=True, default=0.0) # Заработная плата