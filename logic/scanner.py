"""
logic/scanner.py
Escaneo de rutas físicas del sistema de archivos.
Calcula la fecha de última modificación de forma cross-platform (Windows/macOS).
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_last_modified(path: str) -> str:
    """
    Obtiene la fecha de última modificación de una ruta del sistema de archivos.

    Usa os.stat().st_mtime para leer el timestamp y pathlib para compatibilidad
    entre Windows y macOS.

    Args:
        path: Ruta física del directorio o archivo.

    Returns:
        Fecha formateada como "DD/MM/YYYY HH:MM", o mensaje de error si la ruta
        no existe o no es accesible.
    """
    if not path or not path.strip():
        return "Sin ruta"

    p = Path(path)

    if not p.exists():
        return "Ruta no encontrada"

    try:
        mtime = p.stat().st_mtime
        dt = datetime.fromtimestamp(mtime)
        return dt.strftime("%d/%m/%Y %H:%M")
    except PermissionError:
        return "Sin permiso"
    except OSError as exc:
        return f"Error: {exc.strerror}"


def scan_project(proyecto) -> dict:
    """
    Escanea las tres rutas físicas de un proyecto y retorna sus fechas de
    última modificación.

    Args:
        proyecto: Objeto Proyecto (ORM) con atributos ruta_dev, ruta_test, ruta_pro.

    Returns:
        Diccionario con claves 'dev', 'test', 'pro' y sus fechas de modificación.
    """
    return {
        "dev":  get_last_modified(proyecto.ruta_dev or ""),
        "test": get_last_modified(proyecto.ruta_test or ""),
        "pro":  get_last_modified(proyecto.ruta_pro or ""),
    }


def get_folder_size_mb(path: str) -> str:
    """
    Calcula el tamaño total de una carpeta en MB de forma recursiva.
    Usa os.scandir para máximo rendimiento.

    Returns:
        Cadena formateada "X.XX MB", "X.X GB" si supera 1024 MB,
        o un mensaje de error si la ruta no es accesible.
    """
    if not path or not path.strip():
        return "—"

    p = Path(path)
    if not p.exists():
        return "—"

    try:
        total = 0
        for entry in os.scandir(p):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                # Recursión manual para evitar recursión profunda en Python
                stack = [entry.path]
                while stack:
                    current = stack.pop()
                    try:
                        with os.scandir(current) as it:
                            for sub in it:
                                if sub.is_file(follow_symlinks=False):
                                    total += sub.stat().st_size
                                elif sub.is_dir(follow_symlinks=False):
                                    stack.append(sub.path)
                    except PermissionError:
                        pass

        mb = total / (1024 * 1024)
        if mb >= 1024:
            return f"{mb / 1024:.2f} GB"
        return f"{mb:.1f} MB"
    except PermissionError:
        return "Sin permiso"
    except OSError:
        return "Error"


def path_exists(path: Optional[str]) -> bool:
    """
    Comprueba si una ruta existe en el sistema de archivos.

    Args:
        path: Ruta a comprobar (puede ser None o vacía).

    Returns:
        True si la ruta existe y no está vacía, False en cualquier otro caso.
    """
    if not path or not path.strip():
        return False
    return Path(path).exists()


def find_readme(path: str) -> Optional[str]:
    """
    Busca un archivo README.md (case-insensitive) en el directorio indicado.
    Solo busca en el nivel raíz de la ruta (no recursivo).

    Args:
        path: Ruta del directorio donde buscar.

    Returns:
        Ruta absoluta del archivo README encontrado, o None si no existe.
    """
    if not path or not path.strip():
        return None

    p = Path(path)
    if not p.exists() or not p.is_dir():
        return None

    try:
        for entry in p.iterdir():
            if entry.is_file() and entry.name.lower() == "readme.md":
                return str(entry)
    except (PermissionError, OSError):
        pass

    return None
