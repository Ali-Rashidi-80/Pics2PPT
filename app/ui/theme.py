"""Theme palettes and dynamic QSS builder."""

from __future__ import annotations

from app.ui.fonts import FONT_SCALES, font_css_roles

THEME_PALETTES = {
    "dark_cyan": {
        "bg": "#07070c",
        "bg_alt": "#0d0d14",
        "sidebar": "#0a0a11",
        "surface": "#111119",
        "surface_hover": "#181f28",
        "border": "#263340",
        "border_soft": "#1a222c",
        "accent": "#00bcd4",
        "accent_bright": "#4dd0e1",
        "accent_muted": "rgba(0,188,212,0.13)",
        "accent_glow": "rgba(0,188,212,0.28)",
        "text": "#eceff1",
        "text_secondary": "#90a4ae",
        "text_muted": "#607d8b",
        "text_on_accent": "#001015",
        "success": "#00e676",
        "success_muted": "rgba(0,230,118,0.12)",
        "danger": "#ff5252",
        "danger_muted": "rgba(255,82,82,0.14)",
        "tooltip_bg": "#1a2430",
        "tooltip_border": "#00bcd4",
        "tooltip_text": "#f5f5f5",
    },
    "dark_purple": {
        "bg": "#090810",
        "bg_alt": "#0f0d16",
        "sidebar": "#0c0a14",
        "surface": "#15131f",
        "surface_hover": "#211d2e",
        "border": "#3a324f",
        "border_soft": "#282236",
        "accent": "#7c4dff",
        "accent_bright": "#b388ff",
        "accent_muted": "rgba(124,77,255,0.15)",
        "accent_glow": "rgba(124,77,255,0.30)",
        "text": "#ede7f6",
        "text_secondary": "#b39ddb",
        "text_muted": "#7e57c2",
        "text_on_accent": "#ffffff",
        "success": "#69f0ae",
        "success_muted": "rgba(105,240,174,0.12)",
        "danger": "#ff5252",
        "danger_muted": "rgba(255,82,82,0.14)",
        "tooltip_bg": "#1e1a28",
        "tooltip_border": "#7c4dff",
        "tooltip_text": "#f3e5f5",
    },
    "light": {
        "bg": "#eef2f7",
        "bg_alt": "#f8fafc",
        "sidebar": "#ffffff",
        "surface": "#ffffff",
        "surface_hover": "#f1f5f9",
        "border": "#cbd5e1",
        "border_soft": "#e2e8f0",
        "accent": "#0d9488",
        "accent_bright": "#14b8a6",
        "accent_muted": "rgba(13,148,136,0.10)",
        "accent_glow": "rgba(13,148,136,0.22)",
        "text": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "text_on_accent": "#ffffff",
        "success": "#059669",
        "success_muted": "rgba(5,150,105,0.10)",
        "danger": "#dc2626",
        "danger_muted": "rgba(220,38,38,0.10)",
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
    log_bg = "#ffffff" if is_light else "#0c0d12"
    log_fg = "#0f172a" if is_light else "#c8d0d8"
    log_border = p["border_soft"]
    content_bg = p["bg"] if not is_light else p["bg"]
    sidebar_brand_bg = p["sidebar"] if is_light else p["bg_alt"]
    scroll_handle = p["border"] if is_light else "#2a3340"
    scroll_handle_hover = p["accent"] if is_light else p["accent_bright"]

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

/* ── Sidebar ── */
QFrame#SidebarBrand {{
    background: {sidebar_brand_bg};
    border-left: 1px solid {p['border_soft']};
}}
QFrame#SidebarFooter {{
    border-top: 1px solid {p['border_soft']};
    padding-top: 4px;
}}
QLabel#BrandTitle {{
    font-family: {fonts['display']};
    font-size: {f['brand']}px;
    font-weight: 800;
    color: {p['text']};
}}
QLabel#BrandLogo {{
    border-radius: 12px;
    background: {p['accent_muted']};
    padding: 2px;
}}
QLabel#BrandSub {{
    color: {p['text_secondary']};
    font-size: {f['label']}px;
}}
QLabel#SidebarHint {{
    color: {p['text_muted']};
    font-size: {f['caption']}px;
    line-height: 1.4;
}}
QListWidget#Sidebar {{
    background: transparent;
    border: none;
    outline: none;
    padding: 10px 4px;
}}
QListWidget#Sidebar::item {{
    height: 50px;
    padding-right: 16px;
    color: {p['text_secondary']};
    font-weight: 600;
    margin: 4px 8px;
    border-radius: 12px;
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

/* ── Content area ── */
QFrame#ContentArea {{
    background: {content_bg};
    border: none;
}}

/* ── Page headers ── */
QFrame#PageHeader {{ border: none; padding-bottom: 2px; }}
QFrame#PageHeaderAccent {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {p['accent']}, stop:1 transparent);
    border-radius: 2px;
    max-width: 120px;
}}
QLabel#PageTitle {{
    font-family: {fonts['display']};
    font-size: {f['title']}px;
    font-weight: 800;
    color: {p['text']};
    padding-top: 2px;
}}
QLabel#PageSubtitle {{
    color: {p['text_secondary']};
    font-size: {f['label']}px;
    line-height: 1.5;
}}

/* ── Tip card ── */
QFrame#TipCard {{
    background: {p['accent_muted']};
    border: 1px solid {p['border_soft']};
    border-right: 3px solid {p['accent']};
    border-radius: 12px;
}}
QLabel#TipText {{ color: {p['text_secondary']}; font-size: {f['label']}px; }}
QLabel#TipIcon {{ font-size: 16px; }}

/* ── Scroll ── */
QScrollArea, QScrollArea#RtlScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px 2px 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {scroll_handle};
    border-radius: 5px;
    min-height: 32px;
}}
QScrollBar::handle:vertical:hover {{ background: {scroll_handle_hover}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px 4px;
}}
QScrollBar::handle:horizontal {{
    background: {scroll_handle};
    border-radius: 5px;
    min-width: 32px;
}}
QScrollBar::handle:horizontal:hover {{ background: {scroll_handle_hover}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Group boxes ── */
QGroupBox {{
    font-weight: 700;
    border: 1px solid {p['border']};
    border-radius: 12px;
    margin-top: 14px;
    padding: 18px 14px 14px 14px;
    background: {p['surface']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top right;
    right: 14px;
    padding: 0 10px;
    color: {p['accent']};
    background: {p['surface']};
    font-size: {f['label']}px;
}}
QLabel#GroupHint {{
    color: {p['text_muted']};
    font-size: {f['caption']}px;
    padding: 0 2px 6px 2px;
}}
QLabel#FormLabel {{ color: {p['text_secondary']}; font-weight: 600; }}

/* ── Inputs ── */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    border: 1px solid {p['border']};
    border-radius: 10px;
    padding: 9px 12px;
    background: {p['bg_alt'] if not is_light else '#ffffff'};
    color: {p['text']};
    selection-background-color: {p['accent']};
    selection-color: {p['text_on_accent']};
    min-height: 20px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {p['accent']};
    background: {p['surface_hover'] if not is_light else '#ffffff'};
}}
QLineEdit#DropZone {{
    min-height: 46px;
    background: {p['accent_muted']};
    border: 2px dashed {p['border']};
    font-size: {f['label']}px;
}}
QLineEdit#DropZone:focus {{
    border: 2px dashed {p['accent']};
}}
QLineEdit#DropZone[dragOver="true"] {{
    border-color: {p['accent_bright']};
    background: {row_hover};
}}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox QAbstractItemView {{
    background: {p['surface']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 4px;
    selection-background-color: {p['accent_muted']};
    selection-color: {p['accent_bright']};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    width: 22px;
    border: none;
    background: {p['surface_hover']};
    border-radius: 4px;
    margin: 2px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {p['accent_muted']};
}}

/* ── Text areas ── */
QTextEdit, QTextBrowser {{
    border: 1px solid {p['border']};
    border-radius: 10px;
    padding: 10px;
    background: {p['bg_alt'] if not is_light else '#ffffff'};
    color: {p['text']};
}}
QTextEdit#LogView, QTextBrowser#LogView {{
    font-family: {fonts['mono']};
    font-size: {f['caption']}px;
    background: {log_bg};
    color: {log_fg};
    border: 1px solid {log_border};
    border-radius: 8px;
    padding: 10px;
}}
QFrame#LogPanel {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 12px;
}}
QLabel#LogPanelTitle {{
    font-weight: 700;
    color: {p['text_secondary']};
    font-size: {f['label']}px;
}}

/* ── Checkboxes ── */
QCheckBox {{ spacing: 10px; color: {p['text']}; padding: 3px 0; }}
QCheckBox::indicator {{
    width: 20px; height: 20px;
    border-radius: 6px;
    border: 1px solid {p['border']};
    background: {p['bg_alt'] if not is_light else '#ffffff'};
}}
QCheckBox::indicator:hover {{ border-color: {p['accent']}; }}
QCheckBox::indicator:checked {{
    background: {p['accent']};
    border-color: {p['accent']};
}}
QCheckBox:disabled {{ color: {p['text_muted']}; }}

/* ── Buttons ── */
QPushButton {{
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    background: {p['surface_hover']};
    color: {p['text']};
}}
QPushButton:hover {{ background: {p['border_soft']}; }}
QPushButton:pressed {{ padding-top: 11px; padding-bottom: 9px; }}
QPushButton:disabled {{ color: {p['text_muted']}; background: {p['border_soft']}; }}
QPushButton#PrimaryBtn {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {p['accent']}, stop:1 {p['accent_bright']});
    color: {p['text_on_accent']};
    min-width: 130px;
    font-weight: 700;
}}
QPushButton#PrimaryBtn:hover {{ background: {p['accent_bright']}; }}
QPushButton#PrimaryBtn:disabled {{
    background: {p['border_soft']};
    color: {p['text_muted']};
}}
QPushButton#DangerBtn {{
    background: {p['danger']};
    color: #ffffff;
    min-width: 90px;
}}
QPushButton#DangerBtn:hover {{ background: #ff7070; }}
QPushButton#DangerBtn:disabled {{
    background: {p['danger_muted']};
    color: {p['text_muted']};
}}
QPushButton#GhostBtn {{
    background: transparent;
    border: 1px solid {p['border']};
    color: {p['text_secondary']};
    padding: 8px 16px;
}}
QPushButton#GhostBtn:hover {{
    border-color: {p['accent']};
    color: {p['accent_bright']};
    background: {p['accent_muted']};
}}
QPushButton#IconBtn {{
    min-width: 38px;
    max-width: 38px;
    padding: 0;
    background: {p['bg_alt'] if not is_light else '#ffffff'};
    border: 1px solid {p['border']};
    color: {p['text_secondary']};
    font-weight: 700;
    font-size: 16px;
}}
QPushButton#IconBtn:hover {{
    border-color: {p['accent']};
    color: {p['accent_bright']};
    background: {p['accent_muted']};
}}

/* ── Status & progress ── */
QLabel#StatusLabel {{
    font-size: {f['caption']}px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 20px;
}}
QLabel#StatusLabel[state="idle"] {{
    color: {p['text_muted']};
    background: {p['border_soft']};
}}
QLabel#StatusLabel[state="ready"] {{
    color: {p['success']};
    background: {p['success_muted']};
}}
QLabel#StatusLabel[state="running"] {{
    color: {p['accent_bright']};
    background: {p['accent_muted']};
}}
QLabel#StatusLabel[state="error"] {{
    color: {p['danger']};
    background: {p['danger_muted']};
}}
QLabel#ShortcutHint {{
    color: {p['text_muted']};
    font-size: {f['caption']}px;
}}
QProgressBar {{
    border: 1px solid {p['border']};
    border-radius: 10px;
    text-align: center;
    background: {p['bg_alt'] if not is_light else '#ffffff'};
    height: 22px;
    color: {p['text']};
    font-weight: 600;
    font-size: {f['caption']}px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {p['accent']}, stop:1 {p['accent_bright']});
    border-radius: 9px;
}}

/* ── About page ── */
QFrame#AboutHero {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {p['surface']}, stop:1 {p['surface_hover']});
    border: 1px solid {p['border']};
    border-radius: 16px;
}}
QLabel#AboutTitle {{
    font-family: {fonts['display']};
    font-size: {f['title']}px;
    font-weight: 800;
    color: {p['text']};
}}
QLabel#AboutTagline {{ color: {p['text_secondary']}; font-size: {f['label']}px; }}
QLabel#AboutVersion {{
    color: {p['accent_bright']};
    font-size: {f['caption']}px;
    font-weight: 700;
    padding: 4px 10px;
    background: {p['accent_muted']};
    border-radius: 12px;
}}
QLabel#AboutCreator {{ color: {p['text_muted']}; font-size: 10px; }}
QFrame#HelpCard {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 12px;
    padding: 2px;
}}

/* ── Help panel (native RTL widgets) ── */
QWidget#HelpPanel {{
    background: transparent;
}}
QLabel#HelpHeading {{
    color: {p['accent_bright']};
    font-size: {f['title']}px;
    font-weight: 800;
    padding: 4px 0 6px 0;
    border-bottom: 1px solid {p['border']};
}}
QLabel#HelpSubheading {{
    color: {p['text']};
    font-size: {f['label']}px;
    font-weight: 700;
    padding-top: 4px;
}}
QLabel#HelpParagraph, QLabel#HelpBullet, QLabel#HelpNumber {{
    color: {p['text_secondary']};
    font-size: {f['label']}px;
    line-height: 1.7;
}}
QLabel#HelpNumber {{
    color: {p['accent']};
    font-weight: 700;
}}
QFrame#HelpTip {{
    background: {p['accent_muted']};
    border: none;
    border-right: 3px solid {p['accent']};
    border-radius: 10px;
}}
QFrame#HelpWarn {{
    background: {p['surface_hover']};
    border: none;
    border-right: 3px solid {p['border']};
    border-radius: 10px;
}}
QFrame#HelpTable {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 10px;
}}
QLabel#HelpTableHeader {{
    background: {p['surface_hover']};
    color: {p['text']};
    font-weight: 700;
    font-size: {f['label']}px;
    padding: 10px 12px;
    border-bottom: 1px solid {p['border']};
}}
QLabel#HelpTableCell {{
    color: {p['text_secondary']};
    font-size: {f['label']}px;
    padding: 10px 12px;
    border-top: 1px solid {p['border_soft']};
}}
QLabel#HelpPath {{
    color: {p['accent_bright']};
    font-family: {fonts['mono']};
    font-size: {f['caption']}px;
    padding: 2px 0;
}}
QPlainTextEdit#HelpCode {{
    background: {p['surface_hover']};
    color: {p['text_secondary']};
    border: 1px solid {p['border']};
    border-radius: 10px;
    font-family: {fonts['mono']};
    font-size: {f['caption']}px;
    padding: 10px 12px;
}}
"""
