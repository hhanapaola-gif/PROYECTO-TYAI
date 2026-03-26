from fastapi import APIRouter, Query, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.profesor import ProfesorCreate, ProfesorUpdate, ProfesorResponse
from app.database import get_db
import app.services.profesor_service as svc
router = APIRouter(prefix="/profesores", tags=["Profesores"])
@router.get("/stats/resumen", summary="Estadisticas de profesores")
def obtener_estadisticas(db: Session = Depends(get_db)):
    return svc.estadisticas(db)

@router.get("/", response_model=list[ProfesorResponse])
def listar_profesores(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    departamento: Optional[str] = Query(None),
    buscar: Optional[str] = Query(None),
    activo: Optional[bool]= Query(None),
    db: Session = Depends(get_db)
):
    return svc.obtener_todos(db, departamento, buscar, activo, skip, limit)

@router.get("/{profesor_id}", response_model=ProfesorResponse)
def obtener_profesor(profesor_id: int, db: Session = Depends(get_db)):
    return svc.obtener_por_id(db, profesor_id)

@router.post("/", response_model=ProfesorResponse,
status_code=status.HTTP_201_CREATED)
def crear_profesor(prof: ProfesorCreate,
db: Session = Depends(get_db)):
    return svc.crear(db, prof)

@router.put("/{profesor_id}", response_model=ProfesorResponse)
def actualizar_profesor(profesor_id: int, prof: ProfesorCreate,
db: Session = Depends(get_db)):
    return svc.actualizar(db, profesor_id, prof)

@router.patch("/{profesor_id}", response_model=ProfesorResponse)
def actualizar_parcial(profesor_id: int, prof: ProfesorUpdate,
db: Session = Depends(get_db)):
    return svc.actualizar_parcial(db, profesor_id, prof)

@router.patch("/{profesor_id}/estado", response_model=ProfesorResponse)
def cambiar_estado(profesor_id: int,
activo: bool = Query(...),
db: Session = Depends(get_db)):
    return svc.cambiar_estado(db, profesor_id, activo)

@router.delete("/{profesor_id}")
def eliminar_profesor(profesor_id: int,
db: Session = Depends(get_db)):
    return svc.eliminar(db, profesor_id)