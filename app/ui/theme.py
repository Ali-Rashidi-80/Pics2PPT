"""Theme palettes and dynamic QSS builder."""

from __future__ import annotations

from app.ui.fonts import FONT_SCALES, font_css_roles

THEME_PALETTES = {
    "dark_cyan": {
        "bg": "#08080d",
        "bg_alt": "#0e0e14",
        "sidebar": "#0c0c12",
        "surface": "#12121a",
        "surface_hover": "#1a2430",
        "border": "#2a3640",
        "border_soft": "#1e2a32",
        "accent": "#00bcd4",
        "accent_bright": "#4dd0e1",
        "accent_muted": "rgba(0,188,212,0.12)",
        "text": "#eceff1",
        "text_secondary": "#90a4ae",
        "text_muted": "#607d8b",
        "text_on_accent": "#001015",
        "success": "#00e676",
        "danger": "#ff5252",
        "tooltip_bg": "#1a2430",
        "tooltip_border": "#00bcd4",
        "tooltip_text": "#f5f5f5",
    },
    "dark_purple": {
        "bg": "#0a0810",
        "bg_alt": "#100e18",
        "sidebar": "#0e0c16",
        "surface": "#16141f",
        "surface_hover": "#221e2e",
        "border": "#3d3550",
        "border_soft": "#2a2438",
        "accent": "#7c4dff",
        "accent_bright": "#b388ff",
        "accent_muted": "rgba(124,77,255,0.14)",
        "text": "#ede7f6",
        "text_secondary": "#b39ddb",
        "text_muted": "#7e57c2",
        "text_on_accent": "#ffffff",
        "success": "#69f0ae",
        "danger": "#ff5252",
        "tooltip_bg": "#1e1a28",
        "tooltip_border": "#7c4dff",
        "tooltip_text": "#f3e5f5",
    },
    "light": {
        "bg": "#f4f7fb",
        "bg_alt": "#eef2f7",
        "sidebar": "#ffffff",
        "surface": "#ffffff",
        "surface_hover": "#f1f5f9",
        "border": "#cbd5e0",
        "border_soft": "#e2e8f0",
        "accent": "#0d9488",
        "accent_bright": "#14b8a6",
        "accent_muted": "rgba(13,148,136,0.10)",
        "text": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "text_on_accent": "#ffffff",
        "success": "#059669",
        "danger": "#dc2626",
        "tooltip_bg": "#1e293b",
        "tooltip_border": "#14b8a6",
        "tooltip_text": "#f8fafc",
    },
}

THEME_LABELS = {
    "dark_cyan": "تیره فیروزه‌ای",
    "dark_purple": "تیره ارغوانی",
    "light": "روشن",
}


def palette(theme_id: str) -> dict:
    return THEME_PALETTES.get(theme_id, THEME_PALETTES["dark_cyan"])


def build_stylesheet(theme_id: str = "dark_cyan", font_key: str = "medium") -> str:
    p = palette(theme_id)
    f = FONT_SCALES.get(font_key, FONT_SCALES["medium"])
    is_light = theme_id == "light"
    fonts = font_css_roles()
    row_hover = "rgba(13,148,136,0.10)" if is_light else p["accent_muted"]
    log_bg = "#ffffff" if is_light else "#111318"
    log_fg = "#0f172a" if is_light else "#d4d4d4"
    log_border = p["border_soft"]

    return f"""
QMainWindow, QDialog {{ background-color: {p['bg']}; }}
QWidget {{
    font-family: {fonts['ui']};
    font-size: {f['base']}px;
    color: {p['text']};
}}
QToolTip {{
    background-color: {p['tooltip_bg']};
    color: {p['tooltip_text']};
    border: 1px solid {p['tooltip_border']};
    padding: 8px 12px;
    border-radius: 8px;
    font-size: {f['caption']}px;
}}

QFrame#SidebarBrand {{
    background: {p['sidebar']};
    border-left: 1px solid {p['border_soft']};
}}
QLabel#BrandTitle {{
    font-family: {fonts['display']};
    font-size: {f['brand']}px;
    font-weight: 800;
    color: {p['text']};
}}
QLabel#BrandSub {{
    color: {p['text_secondary']};
    font-size: {f['label']}px;
}}
QListWidget#Sidebar {{
    background: transparent;
    border: none;
    outline: none;
    padding: 8px 6px;
}}
QListWidget#Sidebar::item {{
    height: 48px;
    padding-right: 14px;
    color: {p['text_secondary']};
    font-weight: 600;
    margin: 3px 6px;
    border-radius: 10px;
    border: 1px solid transparent;
}}
QListWidget#Sidebar::item:hover {{
    background: {p['accent_muted']};
    color: {p['text']};
    border-color: {p['border']};
}}
QListWidget#Sidebar::item:selected {{
    background: {p['accent_muted']};
    color: {p['accent_bright']};
    border-right: 3px solid {p['accent']};
    font-weight: 700;
}}

QFrame#PageHeader {{ border-bottom: 1px solid {p['border_soft']}; padding-bottom: 6px; }}
QLabel#PageTitle {{
    font-family: {fonts['display']};
    font-size: {f['title']}px;
    font-weight: 800;
    color: {p['text']};
}}
QLabel#PageSubtitle {{ color: {p['text_secondary']}; font-size: {f['label']}px; }}

QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}

QGroupBox {{
    font-weight: 700;
    border: 1px solid {p['border']};
    border-radius: 10px;
    margin-top: 14px;
    padding: 18px 14px 14px 14px;
    background: {p['surface']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top right;
    right: 12px;
    padding: 0 8px;
    color: {p['accent']};
    background: {p['surface']};
}}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 8px 10px;
    background: {p['bg_alt'] if not is_light else '#ffffff'};
    color: {p['text']};
    selection-background-color: {p['accent']};
    selection-color: {p['text_on_accent']};
    min-height: 18px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {p['accent']};
}}
QLineEdit#DropZone {{
    min-height: 42px;
    background: {p['accent_muted']};
    border: 2px dashed {p['border']};
}}
QLineEdit#DropZone[dragOver="true"] {{
    border-color: {p['accent']};
    background: {row_hover};
}}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox QAbstractItemView {{
    background: {p['surface']};
    color: {p['text']};
    border: 1px solid {p['border']};
    selection-background-color: {p['accent_muted']};
}}

QTextEdit, QTextBrowser {{
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 8px;
    background: {p['bg_alt'] if not is_light else '#ffffff'};
    color: {p['text']};
}}
QTextEdit#LogView {{
    font-family: {fonts['mono']};
    font-size: {f['caption']}px;
    background: {log_bg};
    color: {log_fg};
    border: 1px solid {log_border};
}}

QCheckBox {{ spacing: 8px; color: {p['text']}; }}
QCheckBox::indicator {{
    width: 18px; height: 18px;
    border-radius: 4px;
    border: 1px solid {p['border']};
    background: {p['bg_alt'] if not is_light else '#ffffff'};
}}
QCheckBox::indicator:checked {{
    background: {p['accent']};
    border-color: {p['accent']};
}}

QPushButton {{
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
    background: {p['surface_hover']};
    color: {p['text']};
}}
QPushButton:hover {{ background: {p['border_soft']}; }}
QPushButton:disabled {{ color: {p['text_muted']}; background: {p['border_soft']}; }}
QPushButton#PrimaryBtn {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {p['accent']}, stop:1 {p['accent_bright']});
    color: {p['text_on_accent']};
    min-width: 120px;
}}
QPushButton#PrimaryBtn:hover {{ background: {p['accent_bright']}; }}
QPushButton#DangerBtn {{ background: {p['danger']}; color: #ffffff; min-width: 90px; }}
QPushButton#GhostBtn {{
    background: transparent;
    border: 1px solid {p['border']};
    color: {p['text_secondary']};
    padding: 7px 14px;
}}

QProgressBar {{
    border: 1px solid {p['border']};
    border-radius: 8px;
    text-align: center;
    background: {p['bg_alt'] if not is_light else '#ffffff'};
    height: 20px;
    color: {p['text']};
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {p['accent']}, stop:1 {p['accent_bright']});
    border-radius: 7px;
}}

QFrame#AboutHero {{
    background: {p['surface']};
    border: 1px solid {p['border_soft']};
    border-radius: 14px;
    padding: 4px;
}}
QLabel#AboutTitle {{ font-size: {f['title']}px; font-weight: 800; color: {p['text']}; }}
QLabel#AboutTagline {{ color: {p['text_secondary']}; font-size: {f['label']}px; }}
QLabel#AboutCreator {{ color: {p['text_muted']}; font-size: 10px; }}
"""
