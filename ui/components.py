"""
ui/components.py  —  Dev Project Hub
ProjectCard colapsable y estados vacíos. Compatible con Flet 0.25.2.
"""

import flet as ft
import subprocess
import platform
from pathlib import Path
from typing import Callable

from logic.launcher import get_ide_availability, open_in_explorer
from logic.scanner import get_last_modified, get_folder_size_mb, path_exists, find_readme

# ─── Colores ───────────────────────────────────────────────────────────────────
C_CARD      = "#1E1E2E"
C_CARD_HEAD = "#181825"
C_ROW_ALT   = "#2A2A3E"
C_ACCENT    = "#2196F3"
C_SUCCESS   = "#A6E3A1"
C_ERROR     = "#F38BA8"
C_TEXT      = "#CDD6F4"
C_MUTED     = "#6C7086"
C_BORDER    = "#313244"
C_OBS_BG    = "#252535"

# ─── Mapas de iconos ───────────────────────────────────────────────────────────
LANG_ICON = {
    "Python": (ft.Icons.CODE,            "#3776AB"),
    "Nuxt":   (ft.Icons.WEB,             "#00DC82"),
    "Vue":    (ft.Icons.WEB,             "#42B883"),
    "React":  (ft.Icons.WEB,             "#61DAFB"),
    "CSharp": (ft.Icons.DEVELOPER_BOARD, "#512BD4"),
    "Bat":    (ft.Icons.TERMINAL,        "#4EC9B0"),
    "Shell":  (ft.Icons.TERMINAL,        "#F1C40F"),
}

IDE_ICON = {
    "vscode":  (ft.Icons.CODE,            "#007ACC", "VS Code"),
    "pycharm": (ft.Icons.SMART_TOY,       "#21D789", "PyCharm"),
    "vstudio": (ft.Icons.DEVELOPER_BOARD, "#7B2FBE", "Visual Studio"),
}

REPO_ICON = {
    "Git":   (ft.Icons.SOURCE, "#F05032"),
    "Azure": (ft.Icons.CLOUD,  "#0078D4"),
}

TIPO_PROYECTO_ICON = {
    "Empresa":      (ft.Icons.BUSINESS,        "#89B4FA"),
    "Personal":     (ft.Icons.PERSON,          "#CBA6F7"),
    "Educativo":    (ft.Icons.SCHOOL,          "#A6E3A1"),
    "Freelance":    (ft.Icons.WORK_OUTLINE,    "#FAB387"),
    "Capacitación": (ft.Icons.MENU_BOOK,       "#F9E2AF"),
}


def _open_file_native(filepath: str) -> None:
    """Abre un archivo con la aplicación predeterminada del SO."""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(
                ["cmd", "/c", "start", "", filepath],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        elif system == "Darwin":
            subprocess.Popen(["open", filepath])
        else:
            subprocess.Popen(["xdg-open", filepath])
    except Exception:
        pass


# ─── Fila DEV / TEST / PRO ────────────────────────────────────────────────────

def _route_row(label: str, ruta: str, fecha: str, size_mb: str,
               desc: str, lenguaje: str,
               on_open: Callable, on_explorer: Callable,
               on_open_readme: Callable) -> ft.Container:
    """
    Fila de un entorno (DEV/TEST/PRO) con:
    - Etiqueta coloreada
    - Descripción del entorno (si existe)
    - Ruta física
    - Fecha de última modificación
    - Tamaño en MB
    - Botón explorador + botones IDE
    """
    avail      = get_ide_availability(lenguaje)
    ruta_ok    = path_exists(ruta)
    readme_path = find_readme(ruta) if ruta_ok else None
    env_color  = {"DEV": "#89B4FA", "TEST": "#FAB387", "PRO": "#A6E3A1"}.get(label, C_TEXT)

    if not ruta:
        fecha_color = C_MUTED
    elif any(x in fecha for x in ("no encontrada", "Error", "Sin permiso", "Sin ruta")):
        fecha_color = C_ERROR
    else:
        fecha_color = C_SUCCESS

    ruta_display = ruta if ruta else "—"
    if len(ruta_display) > 40:
        ruta_display = "..." + ruta_display[-37:]

    def _ide_btn(key: str) -> ft.IconButton:
        icon, color, tip = IDE_ICON[key]
        enabled = avail[key] and ruta_ok
        return ft.IconButton(
            icon=icon,
            icon_color=color if enabled else C_MUTED,
            tooltip=f"Abrir en {tip}" if enabled else f"{tip} (no disponible)",
            icon_size=16,
            disabled=not enabled,
            on_click=lambda e, k=key, r=ruta, lb=label: on_open(k, r, lb),
        )

    explorer_btn = ft.IconButton(
        icon=ft.Icons.FOLDER_OPEN,
        icon_color="#F0A500" if ruta_ok else C_MUTED,
        tooltip="Abrir en explorador" if ruta_ok else "Ruta no disponible",
        icon_size=16,
        disabled=not ruta_ok,
        on_click=lambda e, r=ruta: on_explorer(r),
    )

    # Fila principal de la ruta
    main_row = ft.Row(
        controls=[
            # Etiqueta entorno
            ft.Container(
                content=ft.Text(label, size=11, weight=ft.FontWeight.BOLD, color=env_color),
                width=38,
            ),
            # Ruta física
            ft.Container(
                content=ft.Text(
                    ruta_display, size=11,
                    color=C_TEXT if ruta_ok else C_MUTED,
                    font_family="monospace",
                    tooltip=ruta or None,
                    no_wrap=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                expand=True,
            ),
            # Fecha
            ft.Container(
                content=ft.Text(fecha, size=10, color=fecha_color, no_wrap=True),
                width=120,
            ),
            # Tamaño
            ft.Container(
                content=ft.Text(size_mb, size=10, color=C_MUTED, no_wrap=True),
                width=72,
                tooltip="Tamaño total de la carpeta",
            ),
            # Botones: explorador + README + IDEs
            ft.Row(
                controls=[
                    explorer_btn,
                    ft.IconButton(
                        icon=ft.Icons.DESCRIPTION_OUTLINED,
                        icon_color="#F9E2AF" if readme_path else C_MUTED,
                        tooltip=f"Abrir README.md ({Path(readme_path).name})" if readme_path else "Sin README.md",
                        icon_size=16,
                        disabled=not readme_path,
                        on_click=lambda e, rp=readme_path: on_open_readme(rp) if rp else None,
                    ),
                    _ide_btn("vscode"), _ide_btn("pycharm"), _ide_btn("vstudio"),
                ],
                spacing=0, tight=True,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    controls = [main_row]

    # Descripción del entorno (opcional, debajo de la fila)
    if desc and desc.strip():
        controls.append(
            ft.Container(
                content=ft.Text(
                    f"  {desc}",
                    size=10, color=C_MUTED, italic=True,
                    no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS,
                ),
                padding=ft.padding.only(left=38, bottom=2),
            )
        )

    return ft.Container(
        content=ft.Column(controls=controls, spacing=1),
        padding=ft.padding.symmetric(horizontal=10, vertical=3),
        bgcolor=C_ROW_ALT if label != "DEV" else None,
        border_radius=4,
    )


# ─── ProjectCard colapsable ───────────────────────────────────────────────────

def build_project_card(proyecto, on_edit: Callable, on_delete: Callable,
                       on_open_url: Callable, on_open_ide: Callable,
                       on_credentials: Callable) -> ft.Card:
    """
    Card colapsable. Por defecto muestra solo la cabecera (modo colapsado).
    Al pulsar la cabecera o el chevron se expande mostrando rutas, tamaños y observación.
    """
    lang_icon, lang_color = LANG_ICON.get(proyecto.lenguaje, (ft.Icons.FOLDER, C_MUTED))
    repo_icon, repo_color = REPO_ICON.get(proyecto.tipo_repo, (ft.Icons.HELP_OUTLINE, C_MUTED))

    # ── Estado de colapso ────────────────────────────────────────────────────
    is_expanded = ft.Ref[bool]()
    is_expanded.current = False

    chevron_icon = ft.Ref[ft.Icon]()

    # ── Calcular datos de escaneo lazy (solo cuando se expande) ──────────────
    _scan_cache: dict = {}

    def _get_scan():
        if not _scan_cache:
            _scan_cache["fechas"] = {
                "DEV":  get_last_modified(proyecto.ruta_dev  or ""),
                "TEST": get_last_modified(proyecto.ruta_test or ""),
                "PRO":  get_last_modified(proyecto.ruta_pro  or ""),
            }
            _scan_cache["sizes"] = {
                "DEV":  get_folder_size_mb(proyecto.ruta_dev  or ""),
                "TEST": get_folder_size_mb(proyecto.ruta_test or ""),
                "PRO":  get_folder_size_mb(proyecto.ruta_pro  or ""),
            }
        return _scan_cache

    # ── Callbacks ────────────────────────────────────────────────────────────
    def on_explorer(ruta: str) -> None:
        open_in_explorer(ruta)

    # ── Cuerpo expandible ────────────────────────────────────────────────────
    body_ref = ft.Ref[ft.Column]()

    def _build_body() -> ft.Column:
        scan = _get_scan()

        def _on_readme(rp: str) -> None:
            _open_file_native(rp)

        rows = [
            _route_row(
                "DEV",  proyecto.ruta_dev  or "", scan["fechas"]["DEV"],
                scan["sizes"]["DEV"],  proyecto.desc_dev  or "",
                proyecto.lenguaje, on_open_ide, on_explorer, _on_readme,
            ),
            _route_row(
                "TEST", proyecto.ruta_test or "", scan["fechas"]["TEST"],
                scan["sizes"]["TEST"], proyecto.desc_test or "",
                proyecto.lenguaje, on_open_ide, on_explorer, _on_readme,
            ),
            _route_row(
                "PRO",  proyecto.ruta_pro  or "", scan["fechas"]["PRO"],
                scan["sizes"]["PRO"],  proyecto.desc_pro  or "",
                proyecto.lenguaje, on_open_ide, on_explorer, _on_readme,
            ),
        ]

        obs = proyecto.observacion or ""
        obs_section = []
        if obs.strip():
            obs_section = [
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.NOTES, size=13, color=C_MUTED),
                        ft.Text(obs, size=11, color=C_MUTED, expand=True,
                                no_wrap=False, max_lines=3,
                                overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.START),
                    bgcolor=C_OBS_BG,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=4,
                    margin=ft.margin.symmetric(horizontal=10, vertical=4),
                )
            ]

        # Barra de acciones
        action_controls = []
        if proyecto.url_github:
            action_controls.append(ft.TextButton(
                text="GitHub", icon=ft.Icons.SOURCE, icon_color="#F05032",
                tooltip=proyecto.url_github,
                on_click=lambda e, u=proyecto.url_github: on_open_url(u),
            ))
        if proyecto.url_azure:
            action_controls.append(ft.TextButton(
                text="Azure", icon=ft.Icons.CLOUD, icon_color="#0078D4",
                tooltip=proyecto.url_azure,
                on_click=lambda e, u=proyecto.url_azure: on_open_url(u),
            ))
        # Botón Docs si hay carpeta de documentación
        ruta_docs = getattr(proyecto, "ruta_docs", None) or ""
        if ruta_docs and path_exists(ruta_docs):
            action_controls.append(ft.TextButton(
                text="Docs", icon=ft.Icons.FOLDER_SPECIAL, icon_color="#CBA6F7",
                tooltip=ruta_docs,
                on_click=lambda e, r=ruta_docs: open_in_explorer(r),
            ))
        action_controls.append(ft.Container(expand=True))
        action_controls.append(ft.TextButton(
            text="Credenciales",
            icon=ft.Icons.KEY,
            icon_color="#F9E2AF",
            style=ft.ButtonStyle(color="#F9E2AF"),
            tooltip="Gestionar credenciales de acceso",
            on_click=lambda e, pid=proyecto.id, nom=proyecto.nombre: on_credentials(pid, nom),
        ))
        action_controls.append(ft.IconButton(
            icon=ft.Icons.EDIT_OUTLINED, icon_color=C_ACCENT,
            tooltip="Editar", icon_size=18,
            on_click=lambda e, pid=proyecto.id: on_edit(pid),
        ))
        action_controls.append(ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE, icon_color=C_ERROR,
            tooltip="Eliminar", icon_size=18,
            on_click=lambda e, pid=proyecto.id: on_delete(pid),
        ))

        return ft.Column(
            controls=[
                ft.Divider(height=1, color=C_BORDER, thickness=1),
                # Subtítulo
                ft.Container(
                    content=ft.Row([
                        ft.Text("Lenguaje: ", size=11, color=C_MUTED),
                        ft.Text(proyecto.lenguaje, size=11, color=lang_color,
                                weight=ft.FontWeight.W_500),
                        ft.Text("  |  Repo: ", size=11, color=C_MUTED),
                        ft.Text(proyecto.tipo_repo, size=11, color=repo_color,
                                weight=ft.FontWeight.W_500),
                        ft.Text("  |  Tipo: ", size=11, color=C_MUTED),
                        ft.Icon(
                            TIPO_PROYECTO_ICON.get(
                                getattr(proyecto, "tipo_proyecto", "Empresa"),
                                (ft.Icons.FOLDER, C_MUTED)
                            )[0],
                            size=13,
                            color=TIPO_PROYECTO_ICON.get(
                                getattr(proyecto, "tipo_proyecto", "Empresa"),
                                (ft.Icons.FOLDER, C_MUTED)
                            )[1],
                        ),
                        ft.Container(width=3),
                        ft.Text(
                            getattr(proyecto, "tipo_proyecto", "Empresa") or "Empresa",
                            size=11,
                            color=TIPO_PROYECTO_ICON.get(
                                getattr(proyecto, "tipo_proyecto", "Empresa"),
                                (ft.Icons.FOLDER, C_MUTED)
                            )[1],
                            weight=ft.FontWeight.W_500,
                        ),
                    ], spacing=0),
                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                ),
                ft.Container(
                    content=ft.Column(controls=rows, spacing=2),
                    padding=ft.padding.symmetric(vertical=4),
                ),
                *obs_section,
                ft.Container(
                    content=ft.Row(controls=action_controls, spacing=2),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border=ft.border.only(top=ft.border.BorderSide(1, C_BORDER)),
                ),
            ],
            spacing=0,
            visible=True,
        )

    body_container = ft.Container(
        content=None,
        visible=False,
    )

    # ── Toggle colapso ────────────────────────────────────────────────────────
    def toggle(e):
        is_expanded.current = not is_expanded.current
        if is_expanded.current:
            # Construir el cuerpo la primera vez (lazy)
            if body_container.content is None:
                body_container.content = _build_body()
            body_container.visible = True
            chevron_icon.current.name = ft.Icons.EXPAND_LESS
        else:
            body_container.visible = False
            chevron_icon.current.name = ft.Icons.EXPAND_MORE
        body_container.update()
        chevron_icon.current.update()

    # ── Cabecera (siempre visible) ────────────────────────────────────────────
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(lang_icon, color=lang_color, size=20),
                    margin=ft.margin.only(right=8),
                ),
                ft.Text(
                    proyecto.nombre, size=14, weight=ft.FontWeight.BOLD,
                    color=C_TEXT, expand=True, no_wrap=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(proyecto.empresa, size=11, color=C_MUTED, italic=True,
                        no_wrap=True),
                ft.Container(width=8),
                # Tipo de proyecto — icono con tooltip
                ft.Icon(
                    TIPO_PROYECTO_ICON.get(
                        getattr(proyecto, "tipo_proyecto", "Empresa"),
                        (ft.Icons.FOLDER, C_MUTED)
                    )[0],
                    size=14,
                    color=TIPO_PROYECTO_ICON.get(
                        getattr(proyecto, "tipo_proyecto", "Empresa"),
                        (ft.Icons.FOLDER, C_MUTED)
                    )[1],
                    tooltip=getattr(proyecto, "tipo_proyecto", "Empresa") or "Empresa",
                ),
                ft.Container(width=6),
                ft.Icon(repo_icon, color=repo_color, size=14,
                        tooltip=proyecto.tipo_repo),
                ft.Container(width=4),
                ft.Icon(
                    ft.Icons.EXPAND_MORE, size=18, color=C_MUTED,
                    ref=chevron_icon,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=C_CARD_HEAD,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=ft.border_radius.only(top_left=8, top_right=8),
        on_click=toggle,
        ink=True,
    )

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[header, body_container],
                spacing=0,
            ),
            bgcolor=C_CARD,
            border_radius=8,
            border=ft.border.all(1, C_BORDER),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        ),
        elevation=3,
        margin=ft.margin.symmetric(vertical=3, horizontal=2),
    )


# ─── Estados vacíos ───────────────────────────────────────────────────────────

def build_empty_state() -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.FOLDER_OPEN, size=64, color=C_MUTED),
                ft.Text("No hay proyectos registrados", size=18, color=C_MUTED,
                        weight=ft.FontWeight.W_500),
                ft.Text("Pulsa el botón '+ Nuevo' para añadir tu primer proyecto.",
                        size=13, color=C_MUTED),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )


def build_no_results_state() -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=C_MUTED),
                ft.Text("Sin resultados", size=16, color=C_MUTED,
                        weight=ft.FontWeight.W_500),
                ft.Text("Prueba con otro término de búsqueda.", size=12, color=C_MUTED),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(40),
    )
