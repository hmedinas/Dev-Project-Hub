"""
ui/about_dialog.py  —  Dev Project Hub
Diálogo "Acerca de" con información de la aplicación.
Compatible con Flet 0.25.2. Usa page.open() / page.close().
"""

import flet as ft

APP_NAME    = "Dev Project Hub"
APP_VERSION = "1.0.0"
APP_DESC    = (
    "Gestor de repositorios y proyectos de desarrollo.\n"
    "Centraliza tus proyectos, rutas físicas, IDEs y credenciales\n"
    "en un único panel de control rápido y visual."
)
APP_AUTHOR  = "Hugo Medina S"
APP_YEAR    = "2026"
APP_STACK   = "Python 3 · Flet 0.25 · SQLite · SQLAlchemy"
APP_LICENSE = "Uso privado — todos los derechos reservados"

C_BG      = "#1E1E2E"
C_SURFACE = "#313244"
C_ACCENT  = "#2196F3"
C_TEXT    = "#CDD6F4"
C_MUTED   = "#6C7086"
C_SUCCESS = "#A6E3A1"


def _row(icon: str, color: str, label: str, value: str) -> ft.Row:
    """Fila de metadato con icono, etiqueta y valor."""
    return ft.Row(
        controls=[
            ft.Icon(icon, size=16, color=color),
            ft.Container(width=8),
            ft.Text(label, size=12, color=C_MUTED, width=90),
            ft.Text(value, size=12, color=C_TEXT, expand=True,
                    weight=ft.FontWeight.W_500),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def build_about_dialog(page: ft.Page) -> ft.AlertDialog:
    """Construye y devuelve el AlertDialog 'Acerca de'."""

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=C_BG,
        shape=ft.RoundedRectangleBorder(radius=12),
        actions_padding=ft.padding.all(0),
        content=ft.Container(
            width=420,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            content=ft.Column(
                spacing=0,
                tight=True,
                controls=[
                    # ── Cabecera con icono + nombre + versión ────────────────
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=ft.Icon(
                                                ft.Icons.HUB,
                                                size=48,
                                                color=C_ACCENT,
                                            ),
                                            bgcolor="#252535",
                                            border_radius=12,
                                            padding=ft.padding.all(12),
                                        ),
                                        ft.Container(width=16),
                                        ft.Column(
                                            controls=[
                                                ft.Text(
                                                    APP_NAME,
                                                    size=20,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=C_TEXT,
                                                ),
                                                ft.Container(
                                                    content=ft.Text(
                                                        f"v{APP_VERSION}",
                                                        size=11,
                                                        color="#1E1E2E",
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    bgcolor=C_ACCENT,
                                                    border_radius=4,
                                                    padding=ft.padding.symmetric(
                                                        horizontal=8, vertical=2
                                                    ),
                                                ),
                                            ],
                                            spacing=6,
                                        ),
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Container(height=12),
                                ft.Text(
                                    APP_DESC,
                                    size=12,
                                    color=C_MUTED,
                                    text_align=ft.TextAlign.LEFT,
                                ),
                            ],
                            spacing=4,
                        ),
                        bgcolor="#252535",
                        border_radius=10,
                        padding=ft.padding.all(16),
                    ),

                    ft.Container(height=12),

                    # ── Metadatos ────────────────────────────────────────────
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                _row(ft.Icons.PERSON_OUTLINE,    "#CBA6F7", "Autor",     APP_AUTHOR),
                                ft.Divider(height=1, color=C_SURFACE),
                                _row(ft.Icons.CALENDAR_TODAY,    "#89B4FA", "Año",       APP_YEAR),
                                ft.Divider(height=1, color=C_SURFACE),
                                _row(ft.Icons.LAYERS_OUTLINED,   "#A6E3A1", "Stack",     APP_STACK),
                                ft.Divider(height=1, color=C_SURFACE),
                                _row(ft.Icons.LOCK_OUTLINE,      "#FAB387", "Licencia",  APP_LICENSE),
                            ],
                            spacing=8,
                        ),
                        bgcolor=C_SURFACE,
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                    ),

                    ft.Container(height=12),

                    # ── Tecnologías usadas (chips) ───────────────────────────
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Tecnologías", size=11, color=C_MUTED,
                                        weight=ft.FontWeight.W_500),
                                ft.Container(height=6),
                                ft.Row(
                                    controls=[
                                        _chip("Python 3",       "#3776AB"),
                                        _chip("Flet 0.25",      "#2196F3"),
                                        _chip("SQLite",         "#44A8C0"),
                                        _chip("SQLAlchemy",     "#D32F2F"),
                                        _chip("Windows / macOS","#A6E3A1"),
                                    ],
                                    wrap=True,
                                    spacing=6,
                                    run_spacing=6,
                                ),
                            ],
                            spacing=0,
                        ),
                        padding=ft.padding.symmetric(horizontal=4),
                    ),

                    ft.Container(height=16),

                    # ── Botón cerrar ─────────────────────────────────────────
                    ft.Divider(height=1, color=C_SURFACE),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    text="Cerrar",
                                    icon=ft.Icons.CLOSE,
                                    bgcolor=C_ACCENT,
                                    color="#FFFFFF",
                                    on_click=lambda e: page.close(dialog),
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.padding.symmetric(
                                            horizontal=24, vertical=10
                                        ),
                                    ),
                                ),
                            ],
                        ),
                        padding=ft.padding.symmetric(horizontal=4, vertical=8),
                    ),
                ],
            ),
        ),
    )

    return dialog


def _chip(label: str, color: str) -> ft.Container:
    """Pequeña etiqueta de tecnología con color de fondo."""
    return ft.Container(
        content=ft.Text(label, size=10, color="#1E1E2E", weight=ft.FontWeight.BOLD),
        bgcolor=color,
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )
