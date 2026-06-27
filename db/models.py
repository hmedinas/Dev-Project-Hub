"""
db/models.py
Definición del modelo ORM para la tabla 'proyectos' usando SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Proyecto(Base):
    """
    Representa un proyecto de desarrollo con sus rutas físicas y metadatos de repositorio.
    """
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificación del proyecto
    nombre = Column(String(200), nullable=False)
    empresa = Column(String(200), nullable=False, default="")

    # Clasificación técnica
    lenguaje = Column(
        String(50),
        nullable=False,
        default="Python"
        # Valores posibles: Python, Nuxt, Vue, React, CSharp, Bat, Shell
    )
    
    # Propiedades virtuales para lenguajes específicos (sin mapear a columnas)
    # Nota: Eliminadas las propiedades virtuales para evitar problemas con SQLAlchemy
    tipo_repo = Column(
        String(20),
        nullable=False,
        default="Git"
        # Valores posibles: Git, Azure
    )
    tipo_proyecto = Column(
        String(50),
        nullable=False,
        default="Empresa"
        # Valores posibles: Empresa, Personal, Educativo, Freelance, Capacitación
    )

    # URLs de repositorios (opcionales)
    url_github_front = Column(String(500), nullable=True)
    url_github_back = Column(String(500), nullable=True)
    url_github_global = Column(String(500), nullable=True)
    url_azure = Column(String(500), nullable=True)  # URL Azure se mantiene a nivel de contenedor

    # Rutas físicas por tipo de proyecto (opcionales, pueden no existir)
    ruta_front = Column(String(1000), nullable=True)
    ruta_back = Column(String(1000), nullable=True)
    ruta_global = Column(String(1000), nullable=True)

    # Ruta física de la carpeta de documentación (opcional)
    ruta_docs = Column(String(1000), nullable=True)

    # Descripción del propósito de cada ruta
    desc_front = Column(String(500), nullable=True)
    desc_back = Column(String(500), nullable=True)
    desc_global = Column(String(500), nullable=True)

    # Observación general del proyecto
    observacion = Column(String(2000), nullable=True)

    # Relación con credenciales
    credenciales = relationship("Credencial", back_populates="proyecto",
                                cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Proyecto id={self.id} nombre='{self.nombre}' lenguaje='{self.lenguaje}'>"

    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario para uso en la UI."""
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "empresa":     self.empresa,
            "lenguaje":    self.lenguaje,
            # Para compatibilidad con la interfaz
            "tipo_repo":   self.tipo_repo,
            "url_github_front":  self.url_github_front  or "",
            "url_github_back":   self.url_github_back   or "",
            "url_github_global": self.url_github_global or "",
            "url_azure":   self.url_azure   or "",
            "tipo_proyecto": self.tipo_proyecto or "Empresa",
            "ruta_front":  self.ruta_front  or "",
            "ruta_back":   self.ruta_back   or "",
            "ruta_global": self.ruta_global or "",
            "ruta_docs":   self.ruta_docs   or "",
            "desc_front":  self.desc_front  or "",
            "desc_back":   self.desc_back   or "",
            "desc_global": self.desc_global or "",
            "observacion": self.observacion or "",
        }


class Credencial(Base):
    """
    Credenciales de acceso asociadas a un proyecto.
    Un proyecto puede tener múltiples credenciales (relación 1:N).
    """
    __tablename__ = "credenciales"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    proyecto_id  = Column(Integer, ForeignKey("proyectos.id"), nullable=False)

    # Tipo de usuario: Administrador, SuperAdministrador, Cliente, Usuario Normal, etc.
    tipo_usuario = Column(String(100), nullable=False, default="Usuario Normal")
    usuario      = Column(String(200), nullable=False, default="")
    password     = Column(String(500), nullable=False, default="")
    notas        = Column(String(1000), nullable=True)

    proyecto = relationship("Proyecto", back_populates="credenciales")

    def __repr__(self) -> str:
        return f"<Credencial id={self.id} tipo='{self.tipo_usuario}' usuario='{self.usuario}'>"

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "proyecto_id":  self.proyecto_id,
            "tipo_usuario": self.tipo_usuario or "",
            "usuario":      self.usuario      or "",
            "password":     self.password     or "",
            "notas":        self.notas        or "",
        }
