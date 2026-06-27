"""
ui/dashboard.py  —  Dev Project Hub
Vista principal. Compatible con Flet 0.25.2.
"""

import webbrowser

import flet as ft

from db import database as db
from logic.launcher import open_in_vscode, open_in_pycharm, open_in_vstudio
from ui.components import build_project_card, build_empty_state, build_no_results_state
from ui.project_form import ProjectForm
from ui.credential_form import CredentialForm
from ui.theme import get_theme_colors


def build_dashboard(page: ft.Page) -> ft.Column:
    # Obtener colores actuales del tema
    colors = get_theme_colors()

    cards_list = ft.ListView(
        expand=True,
        spacing=2,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
    )
    content_area = ft.Container(content=cards_list, expand=True)

    # ── Snackbar ───────────────────────────────────────────────────────────────
    def show_snack(message: str, color: str = colors["C_SUCCESS"]) -> None:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="#1E1E2E"),
            bgcolor=color,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    # ── Callbacks de IDEs ──────────────────────────────────────────────────────
    def on_open_ide(ide: str, ruta: str, label: str) -> None:
        dispatch = {
            "vscode":  open_in_vscode,
            "pycharm": open_in_pycharm,
            "vstudio": open_in_vstudio,
        }
        fn = dispatch.get(ide)
        if fn is None:
            show_snack(f"IDE desconocido: {ide}", colors["C_ERROR"])
            return
        ok, msg = fn(ruta)
        show_snack(msg, colors["C_SUCCESS"] if ok else colors["C_ERROR"])

    def on_open_url(url: str) -> None:
        try:
            webbrowser.open(url)
            show_snack(f"Abriendo: {url[:60]}{'...' if len(url) > 60 else ''}")
        except Exception as exc:
            show_snack(f"No se pudo abrir la URL: {exc}", colors["C_ERROR"])

    # ── Formulario de proyecto ─────────────────────────────────────────────────
    form         = ProjectForm(page, on_save=lambda: refresh(search_field.value or ""))
    cred_form    = CredentialForm(page)

    def on_edit(pid: int) -> None:
        form.open(project_id=pid)

    def on_delete(pid: int) -> None:
        form.open(project_id=pid)

    def on_credentials(pid: int, nombre: str) -> None:
        cred_form.open(proyecto_id=pid, proyecto_nombre=nombre)

    # ── Render ─────────────────────────────────────────────────────────────────
    counter_text = ft.Text("", size=11, color=colors["C_MUTED"])

    def refresh(query: str = "", update: bool = True) -> None:
        proyectos = db.search_projects(query.strip()) if query.strip() else db.get_all_projects()
        total = len(proyectos)
        counter_text.value = (
            f"{total} proyecto{'s' if total != 1 else ''}"
        )
        cards_list.controls.clear()
        if not proyectos:
            content_area.content = (
                build_no_results_state() if db.get_all_projects() else build_empty_state()
            )
        else:
            content_area.content = cards_list
            for p in proyectos:
                cards_list.controls.append(
                    build_project_card(
                        proyecto=p,
                        on_edit=on_edit,
                        on_delete=on_delete,
                        on_open_url=on_open_url,
                        on_open_ide=on_open_ide,
                        on_credentials=on_credentials,
                    )
                )
        if update:
            page.update()

    # ── Barra de búsqueda ──────────────────────────────────────────────────────
    search_field = ft.TextField(
        hint_text="Buscar por nombre, empresa o lenguaje...",
        prefix_icon=ft.Icons.SEARCH,
        border_color=colors["C_SURFACE"],
        focused_border_color=colors["C_ACCENT"],
        hint_style=ft.TextStyle(color=colors["C_MUTED"], size=13),
        text_style=ft.TextStyle(color=colors["C_TEXT"], size=13),
        bgcolor=colors["C_SURFACE"],
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        dense=True,
        expand=True,
        on_change=lambda e: refresh(e.control.value),
        suffix=ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=16,
            icon_color=colors["C_MUTED"],
            tooltip="Limpiar búsqueda",
            on_click=lambda e: _clear_search(),
        ),
    )

    def _clear_search() -> None:
        search_field.value = ""
        search_field.update()
        refresh("")

    toolbar = ft.Container(
        content=ft.Row(
            controls=[
                search_field,
                ft.Container(width=8),
                counter_text,
                ft.Container(width=8),
                ft.ElevatedButton(
                    text="Nuevo",
                    icon=ft.Icons.ADD,
                    bgcolor=colors["C_ACCENT"],
                    color="#FFFFFF",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    ),
                    on_click=lambda e: form.open(),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        bgcolor=colors["C_APPBAR"],
        border=ft.border.only(bottom=ft.border.BorderSide(1, colors["C_SURFACE"])),
    )

    # Carga inicial sin update() — la página aún no tiene este control
    refresh("", update=False)

    return ft.Column(
        controls=[toolbar, content_area],
        expand=True,
        spacing=0,
    )
