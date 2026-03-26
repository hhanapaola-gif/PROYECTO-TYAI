from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.estudiante import Estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate

def _buscar_por_id(db: Session, estudiante_id: int) -> Estudiante:
    """Retorna el objeto ORM o lanza 404."""
    est = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if not est:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {estudiante_id} no encontrado"
        )
    return est

def _validar_duplicados(db: Session, email: str, matricula: str, excluir_id: int = None):
    q = db.query(Estudiante)
    if excluir_id:
        q = q.filter(Estudiante.id != excluir_id)
    
    # ESTAS LÍNEAS DEBEN IR DENTRO DE LA FUNCIÓN (con espacios)
    if q.filter(Estudiante.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un estudiante con el email '{email}'"
        )
    if q.filter(Estudiante.matricula == matricula).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un estudiante con la matricula '{matricula}'"
        )

def obtener_todos(db: Session, carrera=None, buscar=None, activo=None, skip=0, limit=10):
    q = db.query(Estudiante)
    if carrera:
        q = q.filter(Estudiante.carrera == carrera.lower())
    if buscar:
        q = q.filter(Estudiante.nombre.ilike(f"%{buscar}%"))
    if activo is not None:
        q = q.filter(Estudiante.activo == activo)
    return q.offset(skip).limit(limit).all()

def obtener_por_id(db: Session, estudiante_id: int) -> Estudiante:
    return _buscar_por_id(db, estudiante_id)

def crear(db: Session, datos: EstudianteCreate) -> Estudiante:
    _validar_duplicados(db, datos.email, datos.matricula)
    nuevo = Estudiante(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def actualizar(db: Session, estudiante_id: int, datos: EstudianteCreate) -> Estudiante:
    est = _buscar_por_id(db, estudiante_id)
    _validar_duplicados(db, datos.email, datos.matricula, excluir_id=estudiante_id)
    for k, v in datos.model_dump().items():
        setattr(est, k, v)
    db.commit()
    db.refresh(est)
    return est

def actualizar_parcial(db: Session, estudiante_id: int, datos: EstudianteUpdate) -> Estudiante:
    est = _buscar_por_id(db, estudiante_id)
    cambios = datos.model_dump(exclude_unset=True)
    if 'email' in cambios or 'matricula' in cambios:
        _validar_duplicados(
            db,
            cambios.get('email', est.email),
            cambios.get('matricula', est.matricula),
            excluir_id=estudiante_id
        )
    for k, v in cambios.items():
        setattr(est, k, v)
    db.commit()
    db.refresh(est)
    return est

def cambiar_estado(db: Session, estudiante_id: int, activo: bool) -> Estudiante:
    est = _buscar_por_id(db, estudiante_id)
    est.activo = activo
    db.commit()
    db.refresh(est)
    return est

def eliminar(db: Session, estudiante_id: int) -> dict:
    est = _buscar_por_id(db, estudiante_id)
    nombre = est.nombre
    db.delete(est)
    db.commit()
    return {"mensaje": f"Estudiante '{nombre}' eliminado correctamente"}

def estadisticas(db: Session) -> dict:
    from sqlalchemy import func
    total = db.query(Estudiante).count()
    activos = db.query(Estudiante).filter(Estudiante.activo == True).count()
    promedio = db.query(func.avg(Estudiante.promedio)).scalar() or 0
    carreras = {}
    for row in db.query(Estudiante.carrera, func.count(Estudiante.id)).group_by(Estudiante.carrera).all():
        carreras[row[0]] = row[1]
    return {
        "total": total,
        "activos": activos,
        "inactivos": total - activos,
        "promedio_general": round(promedio, 2),
        "por_carrera": carreras
    }