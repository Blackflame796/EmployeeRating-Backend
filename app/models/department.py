# Модель таблицы отделов
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base

class DepartmentModel(Base):
    """Описание структуры отдела в базе данных"""
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True) # Универсальное название отдела
    
    # Связь "один ко многим" с сотрудниками
    employees = relationship("EmployeeModel", back_populates="department")