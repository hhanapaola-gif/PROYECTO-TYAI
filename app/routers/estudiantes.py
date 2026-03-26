
from fastapi import APIRouter, Query, status
from typing import Optional
from app.schemas.estudiante import EstudianteCreate, EstudianteResponse, EstudianteUpdate
import app.services.estudiante_service as svc
router = APIRouter(
    prefix="/estudiantes",
    tags=["Estudiantes"]
)

@router.get("/stats/resumen", summary="Estadísticas generales")
def obtener_estadisticas():
    return svc.estadisticas()


@router.get("/", response_model=list[EstudianteResponse], summary="Listar estudiantes")
def listar_estudiantes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    carrera: Optional[str] = Query(None),
    buscar: Optional[str] = Query(None),
    activo: Optional[bool] = Query(None)
):
    return svc.obtener_todos(carrera, buscar, activo, skip, limit)


@router.get("/{estudiante_id}", response_model=EstudianteResponse, summary="Obtener por ID")
def obtener_estudiante(estudiante_id: int):
    return svc.obtener_por_id(estudiante_id)


@router.post("/", response_model=EstudianteResponse, status_code=status.HTTP_201_CREATED, summary="Crear estudiante")
def crear_estudiante(estudiante: EstudianteCreate):
    return svc.crear(estudiante)


@router.put("/{estudiante_id}", response_model=EstudianteResponse, summary="Actualizar estudiante completo")
def actualizar_estudiante(estudiante_id: int, estudiante: EstudianteCreate):
    """
    PUT reemplaza TODOS los campos.
    Debes enviar todos los datos aunque no cambien.
    """
    return svc.actualizar(estudiante_id, estudiante)


@router.patch("/{estudiante_id}", response_model=EstudianteResponse, summary="Actualizar campos específicos")
def actualizar_parcial(estudiante_id: int, estudiante: EstudianteUpdate):
    """
    PATCH actualiza SOLO los campos que envíes.
    Los campos que no envíes se conservan igual.
    """
    return svc.actualizar_parcial(estudiante_id, estudiante)


@router.patch("/{estudiante_id}/estado", response_model=EstudianteResponse, summary="Activar o desactivar")
def cambiar_estado(estudiante_id: int, activo: bool = Query(..., description="true para activar, false para desactivar")):
    return svc.cambiar_estado(estudiante_id, activo)


@router.delete("/{estudiante_id}", summary="Eliminar estudiante")
def eliminar_estudiante(estudiante_id: int):
    return svc.eliminar(estudiante_id)