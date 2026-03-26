from fastapi import APIRouter, Query, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse
from app.database import get_db
import app.services.estudiante_service as svc
router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])

@router.get("/stats/resumen", summary="Estadisticas de estudiantes")
def obtener_estadisticas(db: Session = Depends(get_db)):
    return svc.estadisticas(db)

@router.get("/", response_model=list[EstudianteResponse])
def listar_estudiantes(
    skip: int = Query(0, ge=0),
limit: int = Query(10, ge=1, le=100),
carrera: Optional[str] = Query(None),
buscar: Optional[str] = Query(None),
activo: Optional[bool]= Query(None),
db: Session = Depends(get_db)
):
    return svc.obtener_todos(db, carrera, buscar, activo, skip, limit)

@router.get("/{estudiante_id}", response_model=EstudianteResponse)
def obtener_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    return svc.obtener_por_id(db, estudiante_id)
@router.post("/", response_model=EstudianteResponse,
status_code=status.HTTP_201_CREATED)

def crear_estudiante(est: EstudianteCreate,
db: Session = Depends(get_db)):
    return svc.crear(db, est)

@router.put("/{estudiante_id}", response_model=EstudianteResponse)
def actualizar_estudiante(estudiante_id: int, est: EstudianteCreate,
db: Session = Depends(get_db)):
    return svc.actualizar(db, estudiante_id, est)

@router.patch("/{estudiante_id}", response_model=EstudianteResponse)
def actualizar_parcial(estudiante_id: int, est: EstudianteUpdate,
db: Session = Depends(get_db)):
    return svc.actualizar_parcial(db, estudiante_id, est)
@router.patch("/{estudiante_id}/estado", response_model=EstudianteResponse)

def cambiar_estado(estudiante_id: int,
activo: bool = Query(...),
db: Session = Depends(get_db)):
    return svc.cambiar_estado(db, estudiante_id, activo)
@router.delete("/{estudiante_id}")

def eliminar_estudiante(estudiante_id: int,
db: Session = Depends(get_db)):
    return svc.eliminar(db, estudiante_id)