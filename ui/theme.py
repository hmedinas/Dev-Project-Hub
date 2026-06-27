"""
ui/theme.py — Dev Project Hub
Definición de temas claro y oscuro para la aplicación.
"""

# Temas oscuro y claro
THEME_DARK = {
    "BG":      "#181825",
    "APPBAR":  "#1E1E2E",
    "ACCENT":  "#2196F3",
    "TEXT":    "#CDD6F4",
    "MUTED":   "#6C7086",
    "SURFACE": "#313244",
    "BORDER":  "#45475A",
    "CARD":    "#1E1E2E",
    "CARD_HEAD": "#181825",
    "ROW_ALT":  "#2A2A3E",
    "ERROR":   "#F38BA8", 
    "SUCCESS": "#A6E3A1",
}

THEME_LIGHT = {
    "BG":      "#FFFFFF",
    "APPBAR":  "#F8F8F8",
    "ACCENT":  "#2196F3",
    "TEXT":    "#333333",
    "MUTED":   "#757575",
    "SURFACE": "#F0F0F0",
    "BORDER":  "#DDDDDD",
    "CARD":    "#FFFFFF",
    "CARD_HEAD": "#F5F5F5",
    "ROW_ALT":  "#F5F5F5",
    "ERROR":   "#F44336",
    "SUCCESS": "#4CAF50",
}

# Tema actual (por defecto claro)
CURRENT_THEME = THEME_LIGHT

def get_theme_colors():
    """Obtiene los colores del tema actual."""
    return {
        "C_BG": CURRENT_THEME["BG"],
        "C_APPBAR": CURRENT_THEME["APPBAR"],
        "C_ACCENT": CURRENT_THEME["ACCENT"],
        "C_TEXT": CURRENT_THEME["TEXT"],
        "C_MUTED": CURRENT_THEME["MUTED"],
        "C_SURFACE": CURRENT_THEME["SURFACE"],
        "C_BORDER": CURRENT_THEME["BORDER"],
        "C_CARD": CURRENT_THEME["CARD"],
        "C_CARD_HEAD": CURRENT_THEME["CARD_HEAD"],
        "C_ROW_ALT": CURRENT_THEME["ROW_ALT"],
        "C_ERROR": CURRENT_THEME["ERROR"],
        "C_SUCCESS": CURRENT_THEME["SUCCESS"],
        "C_OBS_BG": CURRENT_THEME["ROW_ALT"]
    }

def set_theme(is_dark: bool = True):
    """Establece el tema actual."""
    global CURRENT_THEME
    CURRENT_THEME = THEME_DARK if is_dark else THEME_LIGHT