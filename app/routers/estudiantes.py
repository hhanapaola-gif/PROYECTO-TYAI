from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
from datetime import datetime

from app.schemas.estudiante import EstudianteCreate, EstudianteResponse, EstudianteUpdate

router = APIRouter(
    prefix="/estudiantes",
    tags=["Estudiantes"]
)

# ─────────────────────────────────────────
# BASE DE DATOS EN MEMORIA (temporal)
# Semana 4 la reemplazamos con PostgreSQL
# ─────────────────────────────────────────
estudiantes_db = [
    {
        "id": 1,
        "nombre": "Juan Pérez",
        "matricula": "2021001",
        "email": "juan.perez@universidad.edu",
        "carrera": "ingenieria",
        "semestre": 4,
        "promedio": 8.75,
        "telefono": "4421234567",
        "activo": True,
        "fecha_registro": datetime(2021, 8, 15)
    },
    {
        "id": 2,
        "nombre": "María López",
        "matricula": "2021002",
        "email": "maria.lopez@universidad.edu",
        "carrera": "medicina",
        "semestre": 6,
        "promedio": 9.20,
        "telefono": "4429876543",
        "activo": True,
        "fecha_registro": datetime(2021, 8, 15)
    },
    {
        "id": 3,
        "nombre": "Carlos García",
        "matricula": "2021003",
        "email": "carlos.garcia@universidad.edu",
        "carrera": "derecho",
        "semestre": 3,
        "promedio": 7.80,
        "telefono": None,
        "activo": True,
        "fecha_registro": datetime(2021, 8, 15)
    },
    {
        "id": 4,
        "nombre": "Ana Martínez",
        "matricula": "2021004",
        "email": "ana.martinez@universidad.edu",
        "carrera": "ingenieria",
        "semestre": 5,
        "promedio": 9.50,
        "telefono": "4425551234",
        "activo": True,
        "fecha_registro": datetime(2022, 1, 20)
    },
    {
        "id": 5,
        "nombre": "Pedro Sánchez",
        "matricula": "2024305",
        "email": "pedro.sanchez@universidad.edu",
        "carrera": "medicina",
        "semestre": 2,
        "promedio": 8.10,
        "telefono": None,
        "activo": False,
        "fecha_registro": datetime(2024, 8, 10)
    },
]

siguiente_id = 6


# ─────────────────────────────────────────
# GET /estudiantes/stats/resumen
# IMPORTANTE: va ANTES de /{estudiante_id}
# ─────────────────────────────────────────
@router.get("/stats/resumen", summary="Estadísticas generales de estudiantes")
def obtener_estadisticas():
    """
    Retorna estadísticas generales del sistema:
    - Total de estudiantes
    - Activos vs inactivos
    - Promedio general
    - Distribución por carrera
    """
    activos = [e for e in estudiantes_db if e["activo"]]
    inactivos = [e for e in estudiantes_db if not e["activo"]]

    promedios = [e["promedio"] for e in estudiantes_db]
    promedio_general = round(sum(promedios) / len(promedios), 2) if promedios else 0

    carreras = {}
    for e in estudiantes_db:
        carreras[e["carrera"]] = carreras.get(e["carrera"], 0) + 1

    return {
        "total": len(estudiantes_db),
        "activos": len(activos),
        "inactivos": len(inactivos),
        "promedio_general": promedio_general,
        "por_carrera": carreras
    }


# ─────────────────────────────────────────
# GET /estudiantes/
# ─────────────────────────────────────────
@router.get("/", response_model=list[EstudianteResponse], summary="Listar estudiantes")
def listar_estudiantes(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad a retornar"),
    carrera: Optional[str] = Query(None, description="Filtrar por carrera"),
    buscar: Optional[str] = Query(None, description="Buscar por nombre"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo")
):
    """
    Lista estudiantes con paginación y filtros opcionales.

    - **skip**: Cuántos registros saltar (paginación)
    - **limit**: Cuántos retornar (máximo 100)
    - **carrera**: Filtrar por nombre de carrera
    - **buscar**: Buscar por fragmento de nombre
    - **activo**: Filtrar activos (true) o inactivos (false)
    """
    resultado = estudiantes_db

    if carrera:
        resultado = [e for e in resultado if e["carrera"] == carrera.lower()]

    if buscar:
        resultado = [e for e in resultado if buscar.lower() in e["nombre"].lower()]

    if activo is not None:
        resultado = [e for e in resultado if e["activo"] == activo]

    return resultado[skip: skip + limit]


# ─────────────────────────────────────────
# GET /estudiantes/{estudiante_id}
# ─────────────────────────────────────────
@router.get("/{estudiante_id}", response_model=EstudianteResponse, summary="Obtener estudiante por ID")
def obtener_estudiante(estudiante_id: int):
    """
    Retorna un estudiante específico por su ID.
    Lanza 404 si no existe.
    """
    for estudiante in estudiantes_db:
        if estudiante["id"] == estudiante_id:
            return estudiante

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Estudiante con ID {estudiante_id} no encontrado"
    )


# ─────────────────────────────────────────
# POST /estudiantes/
# ─────────────────────────────────────────
@router.post(
    "/",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo estudiante"
)
def crear_estudiante(estudiante: EstudianteCreate):
    """
    Crea un nuevo estudiante.

    **Validaciones automáticas (Pydantic):**
    - Nombre con al menos 2 palabras y sin números
    - Matrícula de exactamente 7 dígitos
    - Email con formato válido
    - Semestre entre 1 y 12
    - Promedio entre 0.0 y 10.0
    - Teléfono de 10 dígitos (opcional)

    **Validaciones de negocio:**
    - Email no duplicado
    - Matrícula no duplicada
    """
    global siguiente_id

    for e in estudiantes_db:
        if e["email"] == estudiante.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un estudiante con el email '{estudiante.email}'"
            )

    for e in estudiantes_db:
        if e["matricula"] == estudiante.matricula:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un estudiante con la matrícula '{estudiante.matricula}'"
            )

    nuevo_estudiante = {
        "id": siguiente_id,
        **estudiante.model_dump(),
        "activo": True,
        "fecha_registro": datetime.now()
    }

    estudiantes_db.append(nuevo_estudiante)
    siguiente_id += 1

    return nuevo_estudiante