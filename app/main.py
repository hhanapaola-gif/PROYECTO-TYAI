from fastapi import FastAPI, Request, Form, Depends # Añadido Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from sqlalchemy.orm import Session # Añadido Session

from app.routers import estudiantes, profesores
import app.services.estudiante_service as est_svc
import app.services.profesor_service as prof_svc

# Importaciones de base de datos
from app.database import engine, Base, get_db # Añadido get_db
from app.models import Estudiante, Profesor

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema Académico API",
    description="API para gestión de estudiantes y profesores",
    version="1.0.0"
)

templates = Jinja2Templates(directory="app/templates")

app.include_router(estudiantes.router)
app.include_router(profesores.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# ══════════════════════════════════════════
# VISTAS HTML — ESTUDIANTES
# ══════════════════════════════════════════

@app.get("/ui", response_class=HTMLResponse)
def ui_inicio(
    request: Request, 
    mensaje: Optional[str] = None, 
    error: Optional[str] = None,
    db: Session = Depends(get_db) # Inyección de BD
):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "estudiantes": est_svc.obtener_todos(db), # Ahora usa la BD
        "stats": est_svc.estadisticas(db),       # Ahora usa la BD
        "mensaje": mensaje,
        "error": error
    })

@app.post("/ui/nuevo")
def ui_crear_estudiante(
    request: Request,
    nombre: str = Form(...),
    matricula: str = Form(...),
    email: str = Form(...),
    carrera: str = Form(...),
    semestre: int = Form(...),
    promedio: float = Form(...),
    telefono: Optional[str] = Form(None),
    db: Session = Depends(get_db) # Inyección de BD
):
    try:
        from app.schemas.estudiante import EstudianteCreate
        datos = EstudianteCreate(
            nombre=nombre, matricula=matricula, email=email,
            carrera=carrera, semestre=semestre, promedio=promedio,
            telefono=telefono or None
        )
        # Pasamos db como primer argumento
        nuevo = est_svc.crear(db, datos) 
        return RedirectResponse(url=f"/ui?mensaje=Estudiante registrado correctamente", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/ui?error={str(e)}", status_code=303)

@app.post("/ui/estudiantes/{estudiante_id}/estado")
def ui_cambiar_estado_estudiante(
    estudiante_id: int, 
    activo: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        est_svc.cambiar_estado(db, estudiante_id, activo == "true")
        return RedirectResponse(url="/ui?mensaje=Estado actualizado correctamente", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/ui?error={str(e)}", status_code=303)

@app.post("/ui/estudiantes/{estudiante_id}/eliminar")
def ui_eliminar_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db)
):
    try:
        resultado = est_svc.eliminar(db, estudiante_id)
        return RedirectResponse(url=f"/ui?mensaje={resultado['mensaje']}", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/ui?error={str(e)}", status_code=303)

# ══════════════════════════════════════════
# VISTAS HTML — PROFESORES
# ══════════════════════════════════════════

@app.get("/ui/profesores", response_class=HTMLResponse)
def ui_profesores(
    request: Request, 
    mensaje: Optional[str] = None, 
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse("profesores.html", {
        "request": request,
        "profesores": prof_svc.obtener_todos(db), # Ahora usa la BD
        "mensaje": mensaje,
        "error": error
    })

@app.post("/ui/profesores/nuevo")
def ui_crear_profesor(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    departamento: str = Form(...),
    especialidad: str = Form(...),
    telefono: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        from app.schemas.profesor import ProfesorCreate
        datos = ProfesorCreate(
            nombre=nombre, email=email,
            departamento=departamento, especialidad=especialidad,
            telefono=telefono or None
        )
        nuevo = prof_svc.crear(db, datos)
        return RedirectResponse(url=f"/ui/profesores?mensaje=Profesor registrado correctamente", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/ui/profesores?error={str(e)}", status_code=303)

@app.post("/ui/profesores/{profesor_id}/estado")
def ui_cambiar_estado_profesor(
    profesor_id: int, 
    activo: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        prof_svc.cambiar_estado(db, profesor_id, activo == "true")
        return RedirectResponse(url="/ui/profesores?mensaje=Estado actualizado correctamente", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/ui/profesores?error={str(e)}", status_code=303)

@app.post("/ui/profesores/{profesor_id}/eliminar")
def ui_eliminar_profesor(
    profesor_id: int,
    db: Session = Depends(get_db)
):
    try:
        resultado = prof_svc.eliminar(db, profesor_id)
        return RedirectResponse(url=f"/ui/profesores?mensaje={resultado['mensaje']}", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/ui/profesores?error={str(e)}", status_code=303)