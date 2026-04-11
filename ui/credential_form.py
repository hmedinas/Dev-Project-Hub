"""
ui/credential_form.py  —  Dev Project Hub
Modal de credenciales. Compatible con Flet 0.25.2.

PATRÓN: page.open(dlg) / page.close(dlg) / page.run_thread(fn)
"""

import flet as ft
from typing import Optional

from db import database as db

TIPOS_USUARIO = [
    "Administrador",
    "SuperAdministrador",
    "Cliente",
    "Usuario Normal",
    "Solo Lectura",
    "Desarrollador",
    "Soporte",
]

C_BG       = "#1E1E2E"
C_SURFACE  = "#313244"
C_SURFACE2 = "#252535"
C_ACCENT   = "#2196F3"
C_ERROR    = "#F38BA8"
C_TEXT     = "#CDD6F4"
C_MUTED    = "#7F849C"

TIPO_COLOR = {
    "Administrador":      "#F38BA8",
    "SuperAdministrador": "#CBA6F7",
    "Cliente":            "#89B4FA",
    "Usuario Normal":     "#A6E3A1",
    "Solo Lectura":       "#6C7086",
    "Desarrollador":      "#FAB387",
    "Soporte":            "#F9E2AF",
}


def _tf(label: str, hint: str = "", password: bool = False) -> ft.TextField:
    return ft.TextField(
        label=label, hint_text=hint,
        password=password,
        can_reveal_password=password,
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


class CredentialForm:
    """Modal de gestión de credenciales para un proyecto."""

    def __init__(self, page: ft.Page) -> None:
        self._page            = page
        self._proyecto_id: Optional[int] = None
        self._proyecto_nombre: str = ""
        self._edit_cred_id: Optional[int] = None

        # ── Campos del formulario ────────────────────────────────────────────
        self.dd_tipo = ft.Dropdown(
            label="Tipo de usuario *",
            options=[ft.dropdown.Option(t) for t in TIPOS_USUARIO],
            value="Usuario Normal",
            border_color=C_SURFACE,
            focused_border_color=C_ACCENT,
            label_style=ft.TextStyle(color=C_MUTED, size=12),
            text_style=ft.TextStyle(color=C_TEXT, size=13),
            bgcolor=C_SURFACE,
            border_radius=6,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=4),
            dense=True,
        )
        self.tf_usuario  = _tf("Usuario *", "admin@ejemplo.com")
        self.tf_password = _tf("Contraseña", "••••••••", password=True)
        self.tf_notas    = ft.TextField(
            label="Notas", hint_text="URL de acceso, entorno, observaciones...",
            multiline=True, min_lines=1, max_lines=3,
            border_color=C_SURFACE, focused_border_color=C_ACCENT,
            label_style=ft.TextStyle(color=C_MUTED, size=12),
            text_style=ft.TextStyle(color=C_TEXT, size=13),
            hint_style=ft.TextStyle(color=C_MUTED, size=12),
            bgcolor=C_SURFACE, border_radius=6,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
            dense=True,
        )
        self._form_error = ft.Text("", color=C_ERROR, size=11)

        # ── Lista dinámica ───────────────────────────────────────────────────
        self._list_col = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

        # ── Título ───────────────────────────────────────────────────────────
        self._title = ft.Text("Credenciales", color=C_TEXT, size=16,
                              weight=ft.FontWeight.BOLD)

        # ── Panel formulario inline ───────────────────────────────────────────
        self._form_title = ft.Text("Nueva credencial", color=C_ACCENT, size=13,
                                   weight=ft.FontWeight.W_500)
        self._btn_save_cred = ft.ElevatedButton(
            text="Guardar",
            icon=ft.Icons.SAVE_OUTLINED,
            bgcolor=C_ACCENT, color="#FFFFFF",
            on_click=self._on_save_cred,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        )
        self._btn_cancel_cred = ft.TextButton(
            text="Cancelar",
            style=ft.ButtonStyle(color=C_MUTED),
            on_click=self._on_cancel_form,
        )
        self._form_panel = ft.Container(
            content=ft.Column([
                ft.Divider(height=1, color=C_SURFACE),
                self._form_title,
                ft.Row([
                    ft.Container(content=self.dd_tipo, expand=1),
                    ft.Container(content=self.tf_usuario, expand=1),
                ], spacing=8),
                ft.Row([
                    ft.Container(content=self.tf_password, expand=1),
                    ft.Container(content=self.tf_notas, expand=1),
                ], spacing=8),
                self._form_error,
                ft.Row([
                    ft.Container(expand=True),
                    self._btn_cancel_cred,
                    self._btn_save_cred,
                ], spacing=4),
            ], spacing=8, tight=True),
            visible=False,
            padding=ft.padding.only(top=8),
        )

        # ── Botón añadir ─────────────────────────────────────────────────────
        self._btn_add = ft.ElevatedButton(
            text="Añadir credencial",
            icon=ft.Icons.ADD,
            bgcolor=C_ACCENT, color="#FFFFFF",
            on_click=self._on_add_click,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        )

        # ── Diálogo principal ─────────────────────────────────────────────────
        self._dialog = ft.AlertDialog(
            modal=True,
            title=self._title,
            bgcolor=C_BG,
            content=ft.Container(
                content=ft.Column([
                    self._list_col,
                    self._form_panel,
                    ft.Divider(height=1, color=C_SURFACE),
                    ft.Row([
                        ft.Container(expand=True),
                        self._btn_add,
                        ft.TextButton(
                            text="Cerrar",
                            style=ft.ButtonStyle(color=C_MUTED),
                            on_click=self._on_close,
                        ),
                    ], spacing=8),
                ], spacing=8, tight=True, width=560,
                   scroll=ft.ScrollMode.AUTO),
                padding=ft.padding.symmetric(horizontal=4, vertical=4),
            ),
            actions_padding=ft.padding.all(0),
            shape=ft.RoundedRectangleBorder(radius=10),
        )

    # ── API pública ────────────────────────────────────────────────────────────

    def open(self, proyecto_id: int, proyecto_nombre: str = "") -> None:
        self._proyecto_id     = proyecto_id
        self._proyecto_nombre = proyecto_nombre
        self._title.value     = f"Credenciales — {proyecto_nombre}" if proyecto_nombre else "Credenciales"
        self._hide_form()
        self._refresh_list()
        self._page.open(self._dialog)

    # ── Render de lista ────────────────────────────────────────────────────────

    def _refresh_list(self) -> None:
        self._list_col.controls.clear()
        if self._proyecto_id is None:
            return
        creds = db.get_credenciales(self._proyecto_id)
        if not creds:
            self._list_col.controls.append(
                ft.Container(
                    content=ft.Text("Sin credenciales registradas.", size=12,
                                    color=C_MUTED, italic=True),
                    padding=ft.padding.symmetric(vertical=8),
                )
            )
            return

        for c in creds:
            # Convertir explícitamente a tipos Python nativos (evita Column[x] de SQLAlchemy)
            cred_id      = int(c.id)
            tipo_text    = str(c.tipo_usuario or "")
            usuario_text = str(c.usuario or "—")
            pw_text      = str(c.password or "")
            notas_text   = str(c.notas or "")
            tipo_color   = TIPO_COLOR.get(tipo_text, C_MUTED)

            pw_ref  = ft.Ref[ft.Text]()
            eye_ref = ft.Ref[ft.IconButton]()
            state   = {"visible": False}

            def _toggle(e, pr=pw_ref, er=eye_ref, pw=pw_text, st=state):
                st["visible"] = not st["visible"]
                pr.current.value = pw if st["visible"] else "••••••••"
                er.current.icon  = ft.Icons.VISIBILITY_OFF if st["visible"] else ft.Icons.VISIBILITY
                pr.current.update()
                er.current.update()

            row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(tipo_text, size=10,
                                        weight=ft.FontWeight.BOLD, color=tipo_color),
                        bgcolor=C_SURFACE2, border_radius=4,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        width=150,
                    ),
                    ft.Container(
                        content=ft.Text(usuario_text, size=12, color=C_TEXT,
                                        no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                        expand=True,
                    ),
                    ft.Text("••••••••", size=12, color=C_MUTED, ref=pw_ref),
                    ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        icon_color=C_MUTED, icon_size=15,
                        tooltip="Mostrar/ocultar",
                        ref=eye_ref,
                        on_click=_toggle,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_color=C_ACCENT, icon_size=15,
                        tooltip="Editar",
                        on_click=lambda e, cid=cred_id: self._on_edit_cred(cid),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=C_ERROR, icon_size=15,
                        tooltip="Eliminar",
                        on_click=lambda e, cid=cred_id: self._confirm_delete_cred(cid),
                    ),
                ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=C_SURFACE2,
                border_radius=6,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
            )

            items: list = [row]
            if notas_text.strip():
                items.append(
                    ft.Container(
                        content=ft.Text(f"  {notas_text}", size=10, color=C_MUTED,
                                        italic=True, no_wrap=False, max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                        padding=ft.padding.only(left=8, bottom=2),
                    )
                )
            self._list_col.controls.append(ft.Column(controls=items, spacing=1))

    # ── Formulario inline ──────────────────────────────────────────────────────

    def _show_form(self, title: str = "Nueva credencial") -> None:
        self._form_title.value   = title
        self._form_panel.visible = True
        self._btn_add.visible    = False
        self._form_error.value   = ""

    def _hide_form(self) -> None:
        self._form_panel.visible  = False
        self._btn_add.visible     = True
        self._edit_cred_id        = None
        self.dd_tipo.value        = "Usuario Normal"
        self.tf_usuario.value     = ""
        self.tf_password.value    = ""
        self.tf_notas.value       = ""
        self._form_error.value    = ""

    def _on_add_click(self, e) -> None:
        self._edit_cred_id = None
        self._hide_form()
        self._show_form("Nueva credencial")
        self._page.update()

    def _on_edit_cred(self, cred_id: int) -> None:
        if self._proyecto_id is None:
            return
        creds = db.get_credenciales(self._proyecto_id)
        cred  = next((c for c in creds if int(c.id) == cred_id), None)
        if cred is None:
            return
        self._edit_cred_id     = cred_id
        self.dd_tipo.value     = str(cred.tipo_usuario or "Usuario Normal")
        self.tf_usuario.value  = str(cred.usuario      or "")
        self.tf_password.value = str(cred.password     or "")
        self.tf_notas.value    = str(cred.notas        or "")
        self._show_form("Editar credencial")
        self._page.update()

    def _on_cancel_form(self, e) -> None:
        self._hide_form()
        self._page.update()

    def _on_save_cred(self, e) -> None:
        self._form_error.value = ""
        usuario = (self.tf_usuario.value or "").strip()
        if not usuario:
            self._form_error.value = "El campo usuario es obligatorio."
            self._form_error.update()
            return

        data = {
            "tipo_usuario": self.dd_tipo.value or "Usuario Normal",
            "usuario":      usuario,
            "password":     (self.tf_password.value or "").strip(),
            "notas":        (self.tf_notas.value or "").strip(),
        }
        try:
            if self._edit_cred_id is not None:
                db.update_credencial(self._edit_cred_id, data)
            elif self._proyecto_id is not None:
                db.create_credencial(self._proyecto_id, data)
        except Exception as exc:
            self._form_error.value = f"Error al guardar: {exc}"
            self._form_error.update()
            return

        self._hide_form()
        self._refresh_list()
        self._page.update()

    def _confirm_delete_cred(self, cred_id: int) -> None:
        """Abre diálogo de confirmación para eliminar una credencial."""

        def _do_delete():
            db.delete_credencial(cred_id)
            self._page.close(confirm)
            self._refresh_list()
            self._page.update()

        confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text("Eliminar credencial", color=C_ERROR),
            bgcolor=C_BG,
            content=ft.Text("¿Seguro que quieres eliminar esta credencial?",
                             color=C_TEXT),
            actions=[
                ft.TextButton(
                    text="Cancelar",
                    style=ft.ButtonStyle(color=C_MUTED),
                    on_click=lambda e: self._page.close(confirm),
                ),
                ft.ElevatedButton(
                    text="Eliminar",
                    icon=ft.Icons.DELETE,
                    bgcolor=C_ERROR, color="#1E1E2E",
                    on_click=lambda e: self._page.run_thread(_do_delete),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                ),
            ],
            shape=ft.RoundedRectangleBorder(radius=10),
        )
        self._page.open(confirm)

    def _on_close(self, e) -> None:
        self._page.close(self._dialog)
