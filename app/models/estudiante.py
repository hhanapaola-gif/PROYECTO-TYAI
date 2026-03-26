from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Estudiante(Base):
    __tablename__ = "estudiantes"

    # TODO ESTO DEBE TENER 4 ESPACIOS DE INDENTACIÓN
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    matricula = Column(String(7), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    carrera = Column(String(50), nullable=False)
    semestre = Column(Integer, nullable=False)
    promedio = Column(Float, nullable=False)
    telefono = Column(String(10), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)