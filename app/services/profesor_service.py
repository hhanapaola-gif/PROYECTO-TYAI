from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.profesor import Profesor
from app.schemas.profesor import ProfesorCreate, ProfesorUpdate

def _buscar_por_id(db: Session, profesor_id: int) -> Profesor:
    prof = db.query(Profesor).filter(Profesor.id == profesor_id).first()
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesor con ID {profesor_id} no encontrado"
    )
    return prof

def _validar_duplicados(db: Session, email: str, excluir_id: int = None):
    q = db.query(Profesor)
    if excluir_id:

        q = q.filter(Profesor.id != excluir_id)
    if q.filter(Profesor.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un profesor con el email '{email}'"
    )

def obtener_todos(db: Session, departamento=None, buscar=None,
activo=None, skip=0, limit=10):
    q = db.query(Profesor)
    if departamento:
        q = q.filter(Profesor.departamento == departamento.lower())
    if buscar:
        q = q.filter(Profesor.nombre.ilike(f"%{buscar}%"))
    if activo is not None:
        q = q.filter(Profesor.activo == activo)
    return q.offset(skip).limit(limit).all()

def obtener_por_id(db: Session, profesor_id: int) -> Profesor:
    return _buscar_por_id(db, profesor_id)

def crear(db: Session, datos: ProfesorCreate) -> Profesor:
    _validar_duplicados(db, datos.email)
    nuevo = Profesor(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def actualizar(db: Session, profesor_id: int,
datos: ProfesorCreate) -> Profesor:
    prof = _buscar_por_id(db, profesor_id)
    _validar_duplicados(db, datos.email, excluir_id=profesor_id)
    for k, v in datos.model_dump().items():
        setattr(prof, k, v)
    db.commit()
    db.refresh(prof)
    return prof

def actualizar_parcial(db: Session, profesor_id: int,
datos: ProfesorUpdate) -> Profesor:
    prof = _buscar_por_id(db, profesor_id)
    cambios = datos.model_dump(exclude_unset=True)
    if 'email' in cambios:
        _validar_duplicados(db, cambios['email'], excluir_id=profesor_id)
    for k, v in cambios.items():
        setattr(prof, k, v)
    db.commit()
    db.refresh(prof)
    return prof

def cambiar_estado(db: Session, profesor_id: int,
activo: bool) -> Profesor:
    prof = _buscar_por_id(db, profesor_id)
    prof.activo = activo
    db.commit()
    db.refresh(prof)
    return prof

def eliminar(db: Session, profesor_id: int) -> dict:
    prof = _buscar_por_id(db, profesor_id)
    nombre = prof.nombre
    db.delete(prof)
    db.commit()
    return {"mensaje": f"Profesor '{nombre}' eliminado correctamente"}

def estadisticas(db: Session) -> dict:
    total = db.query(Profesor).count()
    activos = db.query(Profesor).filter(Profesor.activo == True).count()
    deptos = {}
    from sqlalchemy import func
    for row in db.query(Profesor.departamento,
    func.count(Profesor.id)).group_by(
    Profesor.departamento).all():
        deptos[row[0]] = row[1]
    return {
        "total": total,
        "activos": activos,
        "inactivos": total - activos,
        "por_departamento": deptos
        }

