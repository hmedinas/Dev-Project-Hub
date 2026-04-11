"""
logic/launcher.py
Smart Launch: detecta el lenguaje del proyecto y abre el IDE apropiado.
Usa subprocess.Popen para lanzar el IDE de forma no bloqueante.

Matriz de IDEs por lenguaje:
  Python            → PyCharm (fallback: VS Code)
  Nuxt/Vue/React    → VS Code
  CSharp            → Visual Studio (Windows) / VS Code (macOS)
  Bat/Shell         → VS Code
"""

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

# ─── Constantes ───────────────────────────────────────────────────────────────

SYSTEM = platform.system()  # "Windows" | "Darwin" | "Linux"

# Comandos CLI de cada IDE
IDE_VSCODE = "code"
IDE_PYCHARM_MAC = "charm"
IDE_PYCHARM_WIN_PATHS = [
    r"C:\Program Files\JetBrains\PyCharm Community Edition\bin\pycharm64.exe",
    r"C:\Program Files\JetBrains\PyCharm Professional Edition\bin\pycharm64.exe",
    r"C:\Program Files (x86)\JetBrains\PyCharm Community Edition\bin\pycharm64.exe",
    r"C:\Program Files (x86)\JetBrains\PyCharm Professional Edition\bin\pycharm64.exe",
]
IDE_VSTUDIO_WIN_PATHS = [
    # Visual Studio 2026 (Preview / Community)
    r"C:\Program Files\Microsoft Visual Studio\2026\Community\Common7\IDE\devenv.exe",
    r"C:\Program Files\Microsoft Visual Studio\2026\Professional\Common7\IDE\devenv.exe",
    r"C:\Program Files\Microsoft Visual Studio\2026\Enterprise\Common7\IDE\devenv.exe",
    r"C:\Program Files\Microsoft Visual Studio\2026\Preview\Common7\IDE\devenv.exe",
    # Visual Studio 2022
    r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
    r"C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\IDE\devenv.exe",
    r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\devenv.exe",
    r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
    # Visual Studio 2019 como fallback
    r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\IDE\devenv.exe",
    r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\Common7\IDE\devenv.exe",
]

# Mapeo de lenguajes a IDEs habilitados
# Cada lenguaje indica qué botones deben estar activos: vscode, pycharm, vstudio
LANGUAGE_IDE_MAP: dict[str, dict[str, bool]] = {
    "Bat":     {"vscode": True,  "pycharm": False, "vstudio": False},
    "CSharp":  {"vscode": True,  "pycharm": False, "vstudio": True},
    "Flutter": {"vscode": True,  "pycharm": False, "vstudio": False},
    "Nuxt":    {"vscode": True,  "pycharm": False, "vstudio": False},
    "Python":  {"vscode": True,  "pycharm": True,  "vstudio": False},
    "React":   {"vscode": True,  "pycharm": False, "vstudio": False},
    "Shell":   {"vscode": True,  "pycharm": False, "vstudio": False},
    "Vue":     {"vscode": True,  "pycharm": False, "vstudio": False},
}


def get_ide_availability(lenguaje: str) -> dict[str, bool]:
    """
    Retorna qué IDEs deben estar habilitados para un lenguaje dado.

    Args:
        lenguaje: Nombre del lenguaje del proyecto.

    Returns:
        Diccionario con claves 'vscode', 'pycharm', 'vstudio' y valores booleanos.
    """
    return LANGUAGE_IDE_MAP.get(lenguaje, {"vscode": True, "pycharm": False, "vstudio": False})


def _find_pycharm() -> Optional[str]:
    """
    Localiza el ejecutable de PyCharm en el sistema.
    En macOS usa el comando 'charm'; en Windows busca en rutas conocidas.

    Returns:
        Ruta al ejecutable o None si no se encuentra.
    """
    if SYSTEM == "Darwin":
        return shutil.which(IDE_PYCHARM_MAC)

    # Windows: buscar en rutas conocidas
    for path in IDE_PYCHARM_WIN_PATHS:
        if Path(path).exists():
            return path

    # Fallback: buscar en PATH
    return shutil.which("pycharm64") or shutil.which("pycharm")


def _find_vstudio() -> Optional[str]:
    """
    Localiza devenv.exe en Windows probando:
    1. Rutas conocidas de VS 2026, 2022 y 2019.
    2. vswhere.exe (herramienta oficial de Microsoft para localizar VS).
    3. PATH del sistema.
    En macOS retorna None.
    """
    if SYSTEM != "Windows":
        return None

    # 1. Rutas conocidas
    for path in IDE_VSTUDIO_WIN_PATHS:
        if Path(path).exists():
            return path

    # 2. vswhere.exe — localiza cualquier versión de VS instalada
    vswhere_paths = [
        r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe",
        r"C:\Program Files\Microsoft Visual Studio\Installer\vswhere.exe",
    ]
    for vswhere in vswhere_paths:
        if Path(vswhere).exists():
            try:
                result = subprocess.run(
                    [vswhere, "-latest", "-property", "installationPath"],
                    capture_output=True, text=True, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                install_path = result.stdout.strip()
                if install_path:
                    devenv = Path(install_path) / "Common7" / "IDE" / "devenv.exe"
                    if devenv.exists():
                        return str(devenv)
            except Exception:
                pass

    # 3. PATH del sistema
    return shutil.which("devenv")


def _find_vscode() -> Optional[str]:
    """
    Localiza el ejecutable de VS Code en el sistema.

    Returns:
        Ruta al comando 'code', o None si no está disponible.
    """
    return shutil.which(IDE_VSCODE)


def open_in_explorer(ruta: str) -> Tuple[bool, str]:
    """
    Abre la ruta en el explorador de archivos nativo del sistema operativo.
    Windows → Explorer, macOS → Finder, Linux → xdg-open.
    """
    if not ruta or not ruta.strip():
        return False, "La ruta no está configurada para este entorno."

    path = Path(ruta)
    if not path.exists():
        return False, f"La ruta no existe: {ruta}"

    try:
        if SYSTEM == "Windows":
            subprocess.Popen(
                ["explorer", str(path)],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        elif SYSTEM == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return True, f"Explorador abierto en: {ruta}"
    except OSError as exc:
        return False, f"Error al abrir explorador: {exc.strerror}"


def open_in_vscode(ruta: str) -> Tuple[bool, str]:
    """
    Abre una ruta en Visual Studio Code.

    Args:
        ruta: Ruta del directorio a abrir.

    Returns:
        Tuple (éxito: bool, mensaje: str).
    """
    return _launch_ide("vscode", ruta)


def open_in_pycharm(ruta: str) -> Tuple[bool, str]:
    """
    Abre una ruta en PyCharm.

    Args:
        ruta: Ruta del directorio a abrir.

    Returns:
        Tuple (éxito: bool, mensaje: str).
    """
    return _launch_ide("pycharm", ruta)


def open_in_vstudio(ruta: str) -> Tuple[bool, str]:
    """
    Abre una ruta en Visual Studio.
    En macOS usa VS Code como alternativa automática.

    Args:
        ruta: Ruta del directorio a abrir.

    Returns:
        Tuple (éxito: bool, mensaje: str).
    """
    return _launch_ide("vstudio", ruta)


def _launch_ide(ide: str, ruta: str) -> Tuple[bool, str]:
    """
    Función centralizada que lanza un IDE con la ruta indicada de forma no bloqueante.

    Args:
        ide: Identificador del IDE ('vscode', 'pycharm', 'vstudio').
        ruta: Ruta del directorio a abrir.

    Returns:
        Tuple (éxito: bool, mensaje: str).
    """
    # 1. Validar que la ruta existe
    if not ruta or not ruta.strip():
        return False, "La ruta no está configurada para este entorno."

    path = Path(ruta)
    if not path.exists():
        return False, f"La ruta no existe: {ruta}"

    # 2. Localizar el ejecutable del IDE
    exe: Optional[str] = None
    ide_name = ""

    if ide == "vscode":
        exe = _find_vscode()
        ide_name = "Visual Studio Code"
    elif ide == "pycharm":
        exe = _find_pycharm()
        ide_name = "PyCharm"
    elif ide == "vstudio":
        if SYSTEM == "Darwin":
            # macOS: Visual Studio no disponible, usar VS Code como fallback
            exe = _find_vscode()
            ide_name = "Visual Studio Code (fallback en macOS)"
        else:
            exe = _find_vstudio()
            ide_name = "Visual Studio"

    if exe is None:
        return False, (
            f"{ide_name} no está instalado o no se encontró en el sistema.\n"
            "Asegúrate de que el ejecutable esté en el PATH o en la ruta de instalación estándar."
        )

    # 3. Lanzar el proceso de forma no bloqueante
    try:
        if SYSTEM == "Windows":
            # CREATE_NO_WINDOW evita que aparezca una ventana de consola en Windows
            subprocess.Popen(
                [exe, str(path)],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        else:
            subprocess.Popen([exe, str(path)])

        return True, f"{ide_name} abierto en: {ruta}"

    except FileNotFoundError:
        return False, f"No se pudo ejecutar {ide_name}. Ruta del ejecutable: {exe}"
    except PermissionError:
        return False, f"Sin permisos para ejecutar {ide_name}."
    except OSError as exc:
        return False, f"Error al abrir {ide_name}: {exc.strerror}"
