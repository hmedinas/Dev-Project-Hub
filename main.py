"""
main.py  —  Dev Project Hub
Punto de entrada. Compatible con Flet 0.25.2.
"""

import flet as ft

from db.database import init_db
from ui.dashboard import build_dashboard
from ui.about_dialog import build_about_dialog
from ui.theme import get_theme_colors, set_theme, CURRENT_THEME

APP_TITLE    = "Dev Project Hub"
APP_VERSION  = "1.0.0"


def main(page: ft.Page) -> None:
    init_db()

    # Obtener colores del tema
    colors = get_theme_colors()
    
    page.title      = APP_TITLE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor    = colors["C_BG"]
    page.padding    = 0
    page.spacing    = 0

    page.window.width      = 1200
    page.window.height     = 800
    page.window.min_width  = 1000
    page.window.min_height = 700

    page.theme = ft.Theme(color_scheme_seed=colors["C_ACCENT"])

    # Variable para controlar el tema actual (por defecto claro)
    is_dark_mode = False
    
    # Función para cambiar el tema
    def toggle_theme(e):
        nonlocal is_dark_mode
        is_dark_mode = not is_dark_mode
        
        # Actualizar tema global
        set_theme(is_dark_mode)
        
        # Obtener nuevos colores
        colors = get_theme_colors()
        
        # Actualizar propiedades de página
        page.bgcolor = colors["C_BG"]
        page.theme_mode = ft.ThemeMode.DARK if is_dark_mode else ft.ThemeMode.LIGHT
        
        # Actualizar AppBar
        theme_icon = ft.Icons.LIGHT_MODE if is_dark_mode else ft.Icons.DARK_MODE
        theme_tooltip = "Cambiar a modo claro" if is_dark_mode else "Cambiar a modo oscuro"
        theme_button.icon = theme_icon
        theme_button.tooltip = theme_tooltip
        appbar.bgcolor = colors["C_APPBAR"]
        appbar.title.color = colors["C_TEXT"]
        version_text.color = colors["C_MUTED"]
        
        # Reconstruir el dashboard completo para actualizar todos los colores
        page.controls.clear()
        page.add(build_dashboard(page))
        page.update()
    
    # Construir el diálogo About (una sola instancia reutilizable)
    about_dialog = build_about_dialog(page)

    def open_about(e) -> None:
        page.open(about_dialog)
    
    # Botón para cambiar tema
    theme_button = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        icon_color=colors["C_MUTED"],
        icon_size=20,
        tooltip="Cambiar a modo oscuro",
        on_click=toggle_theme,
        style=ft.ButtonStyle(
            overlay_color={"hovered": colors["C_SURFACE"]},
        ),
    )

    # Referencia al texto de versión para poder actualizarlo
    version_text = ft.Text(
        f"v{APP_VERSION}",
        size=11,
        color=colors["C_MUTED"],
    )
    
    # AppBar con referencias para poder actualizarla
    appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.Icon(ft.Icons.HUB, color=colors["C_ACCENT"], size=24),
            margin=ft.margin.only(left=12),
        ),
        leading_width=44,
        title=ft.Text(APP_TITLE, size=18, weight=ft.FontWeight.BOLD, color=colors["C_TEXT"]),
        bgcolor=colors["C_APPBAR"],
        elevation=0,
        actions=[
            ft.Container(
                content=version_text,
                margin=ft.margin.only(right=4),
            ),
            theme_button,  # Botón para cambiar tema
            ft.IconButton(
                icon=ft.Icons.INFO_OUTLINE,
                icon_color=colors["C_MUTED"],
                icon_size=20,
                tooltip="Acerca de Dev Project Hub",
                on_click=open_about,
                style=ft.ButtonStyle(
                    overlay_color={"hovered": colors["C_SURFACE"]},
                ),
            ),
            ft.Container(width=8),
        ],
    )
    
    page.appbar = appbar

    page.add(build_dashboard(page))
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
