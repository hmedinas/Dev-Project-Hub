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
    url_github = Column(String(500), nullable=True)
    url_azure = Column(String(500), nullable=True)

    # Rutas físicas de los entornos (opcionales, pueden no existir)
    ruta_dev  = Column(String(1000), nullable=True)
    ruta_test = Column(String(1000), nullable=True)
    ruta_pro  = Column(String(1000), nullable=True)

    # Ruta física de la carpeta de documentación (opcional)
    ruta_docs = Column(String(1000), nullable=True)

    # Descripción del propósito de cada ruta
    desc_dev  = Column(String(500), nullable=True)
    desc_test = Column(String(500), nullable=True)
    desc_pro  = Column(String(500), nullable=True)

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
            "tipo_repo":   self.tipo_repo,
            "url_github":  self.url_github  or "",
            "url_azure":   self.url_azure   or "",
            "tipo_proyecto": self.tipo_proyecto or "Empresa",
            "ruta_dev":    self.ruta_dev    or "",
            "ruta_test":   self.ruta_test   or "",
            "ruta_pro":    self.ruta_pro    or "",
            "ruta_docs":   self.ruta_docs   or "",
            "desc_dev":    self.desc_dev    or "",
            "desc_test":   self.desc_test   or "",
            "desc_pro":    self.desc_pro    or "",
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
