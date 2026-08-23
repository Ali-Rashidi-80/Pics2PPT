"""Lightweight plugin hooks for build lifecycle (Phase 4)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HookFn = Callable[..., Any]

HOOK_BEFORE_BUILD = "before_build"
HOOK_AFTER_BUILD = "after_build"
HOOK_AFTER_VALIDATE = "after_validate"
VALID_HOOKS = frozenset({HOOK_BEFORE_BUILD, HOOK_AFTER_BUILD, HOOK_AFTER_VALIDATE})


@dataclass
class PluginRegistry:
    """In-process hook registry. Plugins register callables; failures are isolated."""

    _hooks: dict[str, list[HookFn]] = field(default_factory=dict)

    def register(self, hook_name: str, fn: HookFn) -> None:
        if hook_name not in VALID_HOOKS:
            raise ValueError(f"Unknown hook: {hook_name}")
        self._hooks.setdefault(hook_name, []).append(fn)

    def clear(self, hook_name: str | None = None) -> None:
        if hook_name is None:
            self._hooks.clear()
        else:
            self._hooks.pop(hook_name, None)

    def run(self, hook_name: str, **kwargs: Any) -> list[str]:
        """Run hooks; return list of warning strings from failures."""
        warnings: list[str] = []
        for fn in list(self._hooks.get(hook_name, [])):
            try:
                fn(**kwargs)
            except Exception as exc:
                warnings.append(f"plugin:{hook_name}:{getattr(fn, '__name__', 'fn')}: {exc}")
        return warnings


# Process-wide default registry (apps/tests may replace or clear)
default_registry = PluginRegistry()


def load_plugins_from_dir(directory: Path | str | None = None, *, registry: PluginRegistry | None = None) -> int:
    """
    Load ``*.py`` plugin modules from ``~/.pics2ppt/plugins/``.

    Each module may define ``register(registry)``.
    Returns number of modules successfully loaded.
    """
    reg = registry or default_registry
    root = Path(directory) if directory else Path.home() / ".pics2ppt" / "plugins"
    if not root.is_dir():
        return 0

    loaded = 0
    import importlib.util

    for path in sorted(root.glob("*.py")):
        if path.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"pics2ppt_plugin_{path.stem}", path)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            register = getattr(mod, "register", None)
            if callable(register):
                register(reg)
                loaded += 1
        except Exception:
            continue
    return loaded
