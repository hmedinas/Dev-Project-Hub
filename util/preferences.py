"""
util/preferences.py — Dev Project Hub
Módulo para manejar las preferencias del usuario, como el tema actual.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Ubicación del archivo de preferencias
PREFS_FILE = Path("user_prefs.json")

# Preferencias por defecto
DEFAULT_PREFERENCES = {
    "theme": "light",  # "light" o "dark"
}


def get_preferences() -> Dict[str, Any]:
    """
    Obtiene todas las preferencias del usuario.
    Si no existe el archivo de preferencias, crea uno con los valores predeterminados.
    """
    if not PREFS_FILE.exists():
        save_preferences(DEFAULT_PREFERENCES)
        return DEFAULT_PREFERENCES
    
    try:
        with open(PREFS_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        # Si hay algún error al leer el archivo, usar los valores predeterminados
        return DEFAULT_PREFERENCES


def save_preferences(prefs: Dict[str, Any]) -> None:
    """
    Guarda las preferencias del usuario en el archivo.
    """
    try:
        with open(PREFS_FILE, "w") as file:
            json.dump(prefs, file, indent=2)
    except OSError:
        # Si hay algún error al guardar, simplemente ignorarlo
        pass


def get_preference(key: str, default: Any = None) -> Any:
    """
    Obtiene una preferencia específica.
    Si la clave no existe, devuelve el valor predeterminado.
    """
    prefs = get_preferences()
    return prefs.get(key, default)


def set_preference(key: str, value: Any) -> None:
    """
    Establece una preferencia específica.
    """
    prefs = get_preferences()
    prefs[key] = value
    save_preferences(prefs)


def is_dark_theme() -> bool:
    """
    Comprueba si el tema actual es oscuro.
    """
    return get_preference("theme", "light") == "dark"