"""
ui/project_form.py  —  Dev Project Hub
Modal de alta y edición de proyectos. Compatible con Flet 0.25.2.

PATRÓN CORRECTO Flet 0.25.2:
  - page.open(dlg)   → añade al offstage.controls, abre el diálogo
  - page.close(dlg)  → cierra ESE diálogo específico (estático, no bloquea)
  - page.run_thread(fn) → ejecuta fn en hilo thread-safe para UI updates post-cierre
"""

import flet as ft
from typing import Callable, Optional

from db import database as db

LENGUAJES       = ["Python", "Nuxt", "Vue", "React", "CSharp", "Bat", "Shell"]
TIPOS_REPO      = ["Git", "Azure"]
TIPOS_PROYECTO  = ["Empresa", "Personal", "Educativo", "Freelance", "Capacitación"]

C_BG      = "#1E1E2E"
C_SURFACE = "#313244"
C_ACCENT  = "#2196F3"
C_ERROR   = "#F38BA8"
C_TEXT    = "#CDD6F4"
C_MUTED   = "#7F849C"


def _tf(label: str, hint: str = "", multiline: bool = False) -> ft.TextField:
    return ft.TextField(
        label=label, hint_text=hint,
        multiline=multiline,
        min_lines=1 if not multiline else 2,
        max_lines=1 if not multiline else 5,
        border_color=C_SURFACE,
        focused_border_color=C_ACCENT,
        label_style=ft.TextStyle(color=C_MUTED, size=12),
        text_style=ft.TextStyle(color=C_TEXT, size=13),
        hint_style=ft.TextStyle(color=C_MUTED, size=12),
        bgcolor=C_SURFACE,
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        dense=True,
    )


def _dd(label: str, options: list) -> ft.Dropdown:
    return ft.Dropdown(
        label=label,
        options=[ft.dropdown.Option(o) for o in options],
        border_color=C_SURFACE,
        focused_border_color=C_ACCENT,
        label_style=ft.TextStyle(color=C_MUTED, size=12),
        text_style=ft.TextStyle(color=C_TEXT, size=13),
        bgcolor=C_SURFACE,
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=4),
        dense=True,
    )


class ProjectForm:
    """Formulario modal para crear o editar proyectos."""

    def __init__(self, page: ft.Page, on_save: Callable[[], None]) -> None:
        self._page    = page
        self._on_save = on_save
        self._edit_id: Optional[int] = None

        # ── Campos básicos ────────────────────────────────────────────────────
        self.tf_nombre        = _tf("Nombre *", "Mi Proyecto")
        self.tf_empresa       = _tf("Empresa / Cliente", "Acme Corp")
        self.dd_lenguaje      = _dd("Lenguaje *", LENGUAJES)
        self.dd_lenguaje.value = "Python"
        self.dd_tipo_repo     = _dd("Tipo de Repositorio *", TIPOS_REPO)
        self.dd_tipo_repo.value = "Git"
        self.dd_tipo_proyecto = _dd("Tipo de Proyecto *", TIPOS_PROYECTO)
        self.dd_tipo_proyecto.value = "Empresa"
        self.tf_url_github    = _tf("URL GitHub", "https://github.com/usuario/repo")
        self.tf_url_azure     = _tf("URL Azure DevOps", "https://dev.azure.com/org/repo")

        # ── Rutas + descripciones ─────────────────────────────────────────────
        self.tf_ruta_dev   = _tf("Ruta Dev",  "C:\\Proyectos\\mi-proyecto\\dev")
        self.tf_desc_dev   = _tf("Descripción Dev", "Ej: Entorno de desarrollo local")
        self.tf_ruta_test  = _tf("Ruta Test", "C:\\Proyectos\\mi-proyecto\\test")
        self.tf_desc_test  = _tf("Descripción Test", "Ej: Servidor de pruebas QA")
        self.tf_ruta_pro   = _tf("Ruta Pro",  "C:\\Proyectos\\mi-proyecto\\pro")
        self.tf_desc_pro   = _tf("Descripción Pro", "Ej: Producción / cliente final")

        # ── Ruta documentación ────────────────────────────────────────────────
        self.tf_ruta_docs  = _tf("Ruta Documentación", "C:\\Proyectos\\mi-proyecto\\docs")

        # ── Observación general ───────────────────────────────────────────────
        self.tf_observacion = _tf(
            "Observación general",
            "Notas, dependencias, contexto del proyecto...",
            multiline=True,
        )

        self._error = ft.Text("", color=C_ERROR, size=12)

        # ── FilePicker ────────────────────────────────────────────────────────
        self._active_field: Optional[ft.TextField] = None
        self._picker = ft.FilePicker(on_result=self._on_picked)
        page.overlay.append(self._picker)

        # ── Botones ───────────────────────────────────────────────────────────
        self._btn_delete = ft.TextButton(
            text="Eliminar",
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=C_ERROR,
            style=ft.ButtonStyle(color=C_ERROR),
            on_click=self._on_delete_click,
            visible=False,
        )
        self._btn_cancel = ft.TextButton(
            text="Cancelar",
            style=ft.ButtonStyle(color=C_MUTED),
            on_click=self._on_cancel,
        )
        self._btn_save = ft.ElevatedButton(
            text="Guardar",
            icon=ft.Icons.SAVE_OUTLINED,
            bgcolor=C_ACCENT,
            color="#FFFFFF",
            on_click=self._on_save_click,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        )

        # ── Diálogo principal ─────────────────────────────────────────────────
        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Proyecto", color=C_TEXT, size=16,
                          weight=ft.FontWeight.BOLD),
            bgcolor=C_BG,
            content=ft.Column(
                controls=[
                    self._build_content(),
                    ft.Divider(height=1, color=C_SURFACE),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self._btn_delete,
                                ft.Container(expand=True),
                                self._btn_cancel,
                                self._btn_save,
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.symmetric(horizontal=4, vertical=6),
                    ),
                ],
                spacing=0,
                tight=True,
            ),
            actions_padding=ft.padding.all(0),
            shape=ft.RoundedRectangleBorder(radius=10),
        )

    # ── API pública ────────────────────────────────────────────────────────────

    def open(self, project_id: Optional[int] = None) -> None:
        self._edit_id = project_id
        self._error.value = ""
        if project_id is not None:
            self._load(project_id)
            self._dialog.title = ft.Text("Editar Proyecto", color=C_TEXT, size=16,
                                         weight=ft.FontWeight.BOLD)
            self._btn_delete.visible = True
        else:
            self._reset()
            self._dialog.title = ft.Text("Nuevo Proyecto", color=C_TEXT, size=16,
                                         weight=ft.FontWeight.BOLD)
            self._btn_delete.visible = False
        self._page.open(self._dialog)

    # ── Construcción del formulario ────────────────────────────────────────────

    def _build_content(self) -> ft.Container:
        def folder_btn(field: ft.TextField) -> ft.IconButton:
            return ft.IconButton(
                icon=ft.Icons.FOLDER_OPEN, icon_color=C_ACCENT,
                tooltip="Seleccionar carpeta", icon_size=18,
                on_click=lambda e, f=field: self._pick(f),
            )

        def ruta_block(tf_ruta: ft.TextField, tf_desc: ft.TextField) -> ft.Column:
            return ft.Column([
                ft.Row(
                    controls=[ft.Container(content=tf_ruta, expand=True), folder_btn(tf_ruta)],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                tf_desc,
            ], spacing=4)

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Container(content=self.tf_nombre, expand=2),
                        ft.Container(content=self.tf_empresa, expand=1),
                    ], spacing=10),
                    ft.Row([
                        ft.Container(content=self.dd_lenguaje, expand=1),
                        ft.Container(content=self.dd_tipo_repo, expand=1),
                        ft.Container(content=self.dd_tipo_proyecto, expand=1),
                    ], spacing=10),
                    ft.Row([
                        ft.Container(content=self.tf_url_github, expand=1),
                        ft.Container(content=self.tf_url_azure, expand=1),
                    ], spacing=10),
                    ft.Divider(height=1, color=C_SURFACE),
                    ft.Text("Rutas físicas", size=12, color=C_MUTED,
                            weight=ft.FontWeight.W_500),
                    ruta_block(self.tf_ruta_dev, self.tf_desc_dev),
                    ruta_block(self.tf_ruta_test, self.tf_desc_test),
                    ruta_block(self.tf_ruta_pro, self.tf_desc_pro),
                    ft.Divider(height=1, color=C_SURFACE),
                    ft.Text("Documentación", size=12, color=C_MUTED,
                            weight=ft.FontWeight.W_500),
                    ft.Row(
                        controls=[
                            ft.Container(content=self.tf_ruta_docs, expand=True),
                            folder_btn(self.tf_ruta_docs),
                        ],
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=C_SURFACE),
                    ft.Text("Observación general", size=12, color=C_MUTED,
                            weight=ft.FontWeight.W_500),
                    self.tf_observacion,
                    self._error,
                ],
                spacing=8,
                width=640,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.symmetric(horizontal=4, vertical=4),
        )

    # ── FilePicker ─────────────────────────────────────────────────────────────

    def _pick(self, field: ft.TextField) -> None:
        self._active_field = field
        self._picker.get_directory_path(dialog_title="Seleccionar carpeta")

    def _on_picked(self, e: ft.FilePickerResultEvent) -> None:
        if e.path and self._active_field is not None:
            self._active_field.value = e.path
            self._active_field.update()
        self._active_field = None

    # ── Callbacks ──────────────────────────────────────────────────────────────

    def _on_cancel(self, e) -> None:
        # Cerrar el diálogo específico y listo — no hace falta run_thread
        self._page.close(self._dialog)

    def _on_save_click(self, e) -> None:
        self._error.value = ""
        nombre = (self.tf_nombre.value or "").strip()
        if not nombre:
            self._error.value = "El nombre del proyecto es obligatorio."
            self._error.update()
            return

        data = {
            "nombre":        nombre,
            "empresa":       (self.tf_empresa.value or "").strip(),
            "lenguaje":      self.dd_lenguaje.value or "Python",
            "tipo_repo":     self.dd_tipo_repo.value or "Git",
            "tipo_proyecto": self.dd_tipo_proyecto.value or "Empresa",
            "url_github":    (self.tf_url_github.value or "").strip(),
            "url_azure":     (self.tf_url_azure.value or "").strip(),
            "ruta_dev":      (self.tf_ruta_dev.value or "").strip(),
            "ruta_test":     (self.tf_ruta_test.value or "").strip(),
            "ruta_pro":      (self.tf_ruta_pro.value or "").strip(),
            "ruta_docs":     (self.tf_ruta_docs.value or "").strip(),
            "desc_dev":      (self.tf_desc_dev.value or "").strip(),
            "desc_test":     (self.tf_desc_test.value or "").strip(),
            "desc_pro":      (self.tf_desc_pro.value or "").strip(),
            "observacion":   (self.tf_observacion.value or "").strip(),
        }
        try:
            if self._edit_id is not None:
                db.update_project(self._edit_id, data)
            else:
                db.create_project(data)
        except Exception as exc:
            self._error.value = f"Error al guardar: {exc}"
            self._error.update()
            return

        # Cerrar el diálogo y luego refrescar en hilo thread-safe
        self._page.close(self._dialog)
        self._page.run_thread(self._on_save)

    def _on_delete_click(self, e) -> None:
        if self._edit_id is None:
            return

        # Capturar el ID por valor para la closure
        eid = self._edit_id

        def _do_delete():
            """Ejecutado por run_thread — contexto thread-safe."""
            if eid is not None:
                db.delete_project(eid)
            # Cerrar ambos diálogos y refrescar
            self._page.close(confirm)
            self._page.close(self._dialog)
            self._on_save()

        confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación", color=C_ERROR),
            bgcolor=C_BG,
            content=ft.Text(
                "¿Seguro que quieres eliminar este proyecto?\nEsta acción no se puede deshacer.",
                color=C_TEXT,
            ),
            actions=[
                ft.TextButton(
                    text="Cancelar",
                    style=ft.ButtonStyle(color=C_MUTED),
                    on_click=lambda e: self._page.close(confirm),
                ),
                ft.ElevatedButton(
                    text="Eliminar",
                    icon=ft.Icons.DELETE,
                    bgcolor=C_ERROR,
                    color="#1E1E2E",
                    on_click=lambda e: self._page.run_thread(_do_delete),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                ),
            ],
            shape=ft.RoundedRectangleBorder(radius=10),
        )
        self._page.open(confirm)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _reset(self) -> None:
        for f in (self.tf_nombre, self.tf_empresa, self.tf_url_github, self.tf_url_azure,
                  self.tf_ruta_dev, self.tf_desc_dev,
                  self.tf_ruta_test, self.tf_desc_test,
                  self.tf_ruta_pro, self.tf_desc_pro,
                  self.tf_ruta_docs, self.tf_observacion):
            f.value = ""
        self.dd_lenguaje.value      = "Python"
        self.dd_tipo_repo.value     = "Git"
        self.dd_tipo_proyecto.value = "Empresa"
        self._error.value = ""

    def _load(self, pid: int) -> None:
        p = db.get_project_by_id(pid)
        if p is None:
            return
        self.tf_nombre.value        = p.nombre                          or ""
        self.tf_empresa.value       = p.empresa                         or ""
        self.dd_lenguaje.value      = p.lenguaje                        or "Python"
        self.dd_tipo_repo.value     = p.tipo_repo                       or "Git"
        self.dd_tipo_proyecto.value = getattr(p, "tipo_proyecto", None) or "Empresa"
        self.tf_url_github.value    = p.url_github                      or ""
        self.tf_url_azure.value     = p.url_azure                       or ""
        self.tf_ruta_dev.value      = p.ruta_dev                        or ""
        self.tf_ruta_test.value     = p.ruta_test                       or ""
        self.tf_ruta_pro.value      = p.ruta_pro                        or ""
        self.tf_ruta_docs.value     = getattr(p, "ruta_docs", None)     or ""
        self.tf_desc_dev.value      = p.desc_dev                        or ""
        self.tf_desc_test.value     = p.desc_test                       or ""
        self.tf_desc_pro.value      = p.desc_pro                        or ""
        self.tf_observacion.value   = p.observacion                     or ""
        self._error.value = ""
