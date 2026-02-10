"""Shared tkinter base helpers for frontend views.

Exports `tk`, `ttk`, `messagebox`, and a safe `BaseFrame` class so the
individual view modules can import them without duplicating the try/except
logic and so imports work in headless CI.
"""
from __future__ import annotations

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except Exception:  # pragma: no cover - allow import in headless CI
    tk = None
    ttk = None
    messagebox = None

# Use a safe base class for frames so module import works even if tkinter
# isn't available. The __init__ of each frame will raise a helpful error
# if the GUI runtime is missing.
BaseFrame = tk.Frame if tk is not None and hasattr(tk, "Frame") else object

from typing import Callable, Optional

__all__ = ["tk", "ttk", "messagebox", "BaseFrame"]
