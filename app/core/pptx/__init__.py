"""PPTX generation package — Hybrid Smart engine."""

from .code_layout import build_presentation
from .com_postprocess import com_postprocess_pptx, powerpoint_available
from .engine import BuildPath, BuildResult, HybridEngine, build_presentation_from_job
from .libreoffice_preview import export_preview, libreoffice_available
from .plugins import PluginRegistry, default_registry, load_plugins_from_dir
from .presets import apply_preset_to_mapping, list_builtin_presets
from .template_analyzer import analyze_template
from .template_import import import_template, layout_wizard_report
from .template_loader import TemplateLoader, bundled_template_if_available
from .validator import validate_pptx, write_build_report

__all__ = [
    "BuildPath",
    "BuildResult",
    "HybridEngine",
    "PluginRegistry",
    "TemplateLoader",
    "analyze_template",
    "apply_preset_to_mapping",
    "build_presentation",
    "build_presentation_from_job",
    "bundled_template_if_available",
    "com_postprocess_pptx",
    "default_registry",
    "export_preview",
    "import_template",
    "layout_wizard_report",
    "libreoffice_available",
    "list_builtin_presets",
    "load_plugins_from_dir",
    "powerpoint_available",
    "validate_pptx",
    "write_build_report",
]
