"""
db/database.py
Configuración del engine SQLite y gestión de sesiones SQLAlchemy.
Proporciona funciones CRUD para la tabla 'proyectos'.
"""

from pathlib import Path
from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from db.models import Base, Proyecto, Credencial

# ─── Configuración del engine ──────────────────────────────────────────────────

# El archivo projects.db se guarda en el mismo directorio que el ejecutable
_DB_PATH = Path(__file__).parent.parent / "projects.db"
_ENGINE = create_engine(f"sqlite:///{_DB_PATH}", echo=False)
_SessionFactory = sessionmaker(bind=_ENGINE)


def init_db() -> None:
    """
    Crea la tabla si no existe y aplica migraciones ligeras para columnas nuevas.
    SQLite no soporta ALTER TABLE ADD COLUMN IF NOT EXISTS, así que comprobamos
    manualmente con PRAGMA table_info.
    """
    Base.metadata.create_all(_ENGINE)

    # Columnas añadidas en versiones posteriores — migración segura
    _new_columns = [
        ("desc_dev",       "VARCHAR(500)"),
        ("desc_test",      "VARCHAR(500)"),
        ("desc_pro",       "VARCHAR(500)"),
        ("observacion",    "VARCHAR(2000)"),
        ("tipo_proyecto",  "VARCHAR(50) DEFAULT 'Empresa'"),
        ("ruta_docs",      "VARCHAR(1000)"),
    ]
    with _ENGINE.connect() as conn:
        from sqlalchemy import text
        existing = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(proyectos)"))
        }
        for col_name, col_type in _new_columns:
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE proyectos ADD COLUMN {col_name} {col_type}"))
        conn.commit()


def get_session() -> Session:
    """Retorna una nueva sesión de base de datos."""
    return _SessionFactory()


# ─── CRUD ──────────────────────────────────────────────────────────────────────

def get_all_projects() -> List[Proyecto]:
    """Retorna todos los proyectos ordenados por nombre."""
    with get_session() as session:
        return session.query(Proyecto).order_by(Proyecto.nombre).all()


def get_project_by_id(project_id: int) -> Optional[Proyecto]:
    """Retorna un proyecto por su ID, o None si no existe."""
    with get_session() as session:
        return session.get(Proyecto, project_id)


def create_project(data: dict) -> Proyecto:
    """
    Crea un nuevo proyecto en la base de datos.

    Args:
        data: Diccionario con los campos del proyecto.

    Returns:
        El objeto Proyecto creado (con ID asignado).
    """
    with get_session() as session:
        proyecto = Proyecto(
            nombre=data["nombre"],
            empresa=data.get("empresa", ""),
            lenguaje=data.get("lenguaje", "Python"),
            tipo_repo=data.get("tipo_repo", "Git"),
            tipo_proyecto=data.get("tipo_proyecto", "Empresa"),
            url_github=data.get("url_github") or None,
            url_azure=data.get("url_azure") or None,
            ruta_dev=data.get("ruta_dev") or None,
            ruta_test=data.get("ruta_test") or None,
            ruta_pro=data.get("ruta_pro") or None,
            ruta_docs=data.get("ruta_docs") or None,
            desc_dev=data.get("desc_dev") or None,
            desc_test=data.get("desc_test") or None,
            desc_pro=data.get("desc_pro") or None,
            observacion=data.get("observacion") or None,
        )
        session.add(proyecto)
        session.commit()
        session.refresh(proyecto)
        return proyecto


def update_project(project_id: int, data: dict) -> Optional[Proyecto]:
    """
    Actualiza un proyecto existente.

    Args:
        project_id: ID del proyecto a actualizar.
        data: Diccionario con los campos a actualizar.

    Returns:
        El objeto Proyecto actualizado, o None si no se encontró.
    """
    with get_session() as session:
        proyecto = session.get(Proyecto, project_id)
        if proyecto is None:
            return None

        proyecto.nombre        = data.get("nombre", proyecto.nombre)
        proyecto.empresa       = data.get("empresa", proyecto.empresa)
        proyecto.lenguaje      = data.get("lenguaje", proyecto.lenguaje)
        proyecto.tipo_repo     = data.get("tipo_repo", proyecto.tipo_repo)
        proyecto.tipo_proyecto = data.get("tipo_proyecto", proyecto.tipo_proyecto)
        proyecto.url_github    = data.get("url_github") or None
        proyecto.url_azure     = data.get("url_azure") or None
        proyecto.ruta_dev      = data.get("ruta_dev") or None
        proyecto.ruta_test     = data.get("ruta_test") or None
        proyecto.ruta_pro      = data.get("ruta_pro") or None
        proyecto.ruta_docs     = data.get("ruta_docs") or None
        proyecto.desc_dev      = data.get("desc_dev") or None
        proyecto.desc_test     = data.get("desc_test") or None
        proyecto.desc_pro      = data.get("desc_pro") or None
        proyecto.observacion   = data.get("observacion") or None

        session.commit()
        session.refresh(proyecto)
        return proyecto


def delete_project(project_id: int) -> bool:
    """
    Elimina un proyecto por su ID.

    Returns:
        True si se eliminó, False si no se encontró.
    """
    with get_session() as session:
        proyecto = session.get(Proyecto, project_id)
        if proyecto is None:
            return False
        session.delete(proyecto)
        session.commit()
        return True


def search_projects(query: str) -> List[Proyecto]:
    """
    Busca proyectos por nombre, empresa o lenguaje (búsqueda insensible a mayúsculas).

    Args:
        query: Texto a buscar.

    Returns:
        Lista de proyectos que coinciden con la búsqueda.
    """
    q = f"%{query.lower()}%"
    with get_session() as session:
        return (
            session.query(Proyecto)
            .filter(
                Proyecto.nombre.ilike(q)
                | Proyecto.empresa.ilike(q)
                | Proyecto.lenguaje.ilike(q)
            )
            .order_by(Proyecto.nombre)
            .all()
        )


# ─── CRUD Credenciales ─────────────────────────────────────────────────────────

def get_credenciales(proyecto_id: int) -> List[Credencial]:
    """Retorna todas las credenciales de un proyecto ordenadas por tipo."""
    with get_session() as session:
        return (
            session.query(Credencial)
            .filter(Credencial.proyecto_id == proyecto_id)
            .order_by(Credencial.tipo_usuario)
            .all()
        )


def create_credencial(proyecto_id: int, data: dict) -> Credencial:
    """Crea una nueva credencial asociada a un proyecto."""
    with get_session() as session:
        cred = Credencial(
            proyecto_id=proyecto_id,
            tipo_usuario=data.get("tipo_usuario", "Usuario Normal"),
            usuario=data.get("usuario", ""),
            password=data.get("password", ""),
            notas=data.get("notas") or None,
        )
        session.add(cred)
        session.commit()
        session.refresh(cred)
        return cred


def update_credencial(cred_id: int, data: dict) -> Optional[Credencial]:
    """Actualiza una credencial existente."""
    with get_session() as session:
        cred = session.get(Credencial, cred_id)
        if cred is None:
            return None
        cred.tipo_usuario = data.get("tipo_usuario", cred.tipo_usuario)
        cred.usuario      = data.get("usuario", cred.usuario)
        cred.password     = data.get("password", cred.password)
        cred.notas        = data.get("notas") or None
        session.commit()
        session.refresh(cred)
        return cred


def delete_credencial(cred_id: int) -> bool:
    """Elimina una credencial por su ID."""
    with get_session() as session:
        cred = session.get(Credencial, cred_id)
        if cred is None:
            return False
        session.delete(cred)
        session.commit()
        return True
