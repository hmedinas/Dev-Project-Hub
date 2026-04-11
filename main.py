"""
main.py  —  Dev Project Hub
Punto de entrada. Compatible con Flet 0.25.2.
"""

import flet as ft

from db.database import init_db
from ui.dashboard import build_dashboard
from ui.about_dialog import build_about_dialog

APP_TITLE    = "Dev Project Hub"
APP_VERSION  = "1.0.0"
COLOR_BG     = "#181825"
COLOR_APPBAR = "#1E1E2E"
COLOR_ACCENT = "#2196F3"
COLOR_TEXT   = "#CDD6F4"
COLOR_MUTED  = "#6C7086"


def main(page: ft.Page) -> None:
    init_db()

    page.title      = APP_TITLE
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor    = COLOR_BG
    page.padding    = 0
    page.spacing    = 0

    page.window.width      = 1200
    page.window.height     = 800
    page.window.min_width  = 1000
    page.window.min_height = 700

    page.theme = ft.Theme(color_scheme_seed=COLOR_ACCENT)

    # Construir el diálogo About (una sola instancia reutilizable)
    about_dialog = build_about_dialog(page)

    def open_about(e) -> None:
        page.open(about_dialog)

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.Icon(ft.Icons.HUB, color=COLOR_ACCENT, size=24),
            margin=ft.margin.only(left=12),
        ),
        leading_width=44,
        title=ft.Text(APP_TITLE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
        bgcolor=COLOR_APPBAR,
        elevation=0,
        actions=[
            ft.Container(
                content=ft.Text(
                    f"v{APP_VERSION}",
                    size=11,
                    color=COLOR_MUTED,
                ),
                margin=ft.margin.only(right=4),
            ),
            ft.IconButton(
                icon=ft.Icons.INFO_OUTLINE,
                icon_color=COLOR_MUTED,
                icon_size=20,
                tooltip="Acerca de Dev Project Hub",
                on_click=open_about,
                style=ft.ButtonStyle(
                    overlay_color={"hovered": "#313244"},
                ),
            ),
            ft.Container(width=8),
        ],
    )

    page.add(build_dashboard(page))
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
