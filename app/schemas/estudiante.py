from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class EstudianteBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    matricula: str = Field(..., pattern=r"^\d{7}$")
    email: EmailStr = Field(...)
    carrera: str = Field(..., min_length=3, max_length=50)
    semestre: int = Field(..., ge=1, le=12)
    promedio: float = Field(..., ge=0.0, le=10.0)
    telefono: Optional[str] = Field(None, pattern=r"^\d{10}$")

    @field_validator("carrera")
    @classmethod
    def normalizar_carrera(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        if any(char.isdigit() for char in v):
            raise ValueError("El nombre no puede contener números")
        if len(v.split()) < 2:
            raise ValueError("Debe incluir nombre y apellido")
        return v.strip().title()

    @field_validator("promedio")
    @classmethod
    def redondear_promedio(cls, v: float) -> float:
        return round(v, 2)

class EstudianteCreate(EstudianteBase):
    pass

class EstudianteResponse(EstudianteBase):
    id: int
    activo: bool
    fecha_registro: datetime
    model_config = {"from_attributes": True}

class EstudianteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    carrera: Optional[str] = Field(None, min_length=3, max_length=50)
    semestre: Optional[int] = Field(None, ge=1, le=12)
    promedio: Optional[float] = Field(None, ge=0.0, le=10.0)
    telefono: Optional[str] = Field(None, pattern=r"^\d{10}$")
    activo: Optional[bool] = None

    @field_validator("carrera")
    @classmethod
    def normalizar_carrera(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip().lower()
        return v