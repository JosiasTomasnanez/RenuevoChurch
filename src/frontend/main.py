from __future__ import annotations

from src.backend.app.main import create_app
from src.frontend.controllers.person_controller import get_controller
from src.frontend.controllers.config_controller import ConfigController
from src.frontend.views.person_view import AddPersonFrame, SearchPersonFrame, ModifyPersonFrame
from src.frontend.views.config_view import ConfigurationFrame
from src.backend.services.config import ConfigService


def _build_main_window(app):
    """Create and return a configured Tk main window instance."""
    import tkinter as tk

    class MainWindow(tk.Tk):
        def __init__(self, app):
            super().__init__()
            self.title("Renuevo — Administración")
            self.geometry("900x600")

            self.app = app
            self.controller = get_controller(app.services)

            # --- ConfigController en vez de servicio directo ---
            self._config_service = ConfigService()
            self.config_controller = ConfigController(self._config_service)

            self._build_ui()

        def _build_ui(self):
            top = tk.Frame(self)
            top.pack(side="top", fill="x", pady=8)

            # Left button for configuration
            self.btn_config = tk.Button(
                top,
                text="Configurar",
                command=lambda: self.show("config"),
                width=12,
                fg="darkblue"
            )
            self.btn_config.pack(side="left", padx=8, pady=0)

            # Centered buttons
            btn_frame = tk.Frame(top)
            btn_frame.pack(anchor="n", expand=True)

            self.btn_add = tk.Button(btn_frame, text="Agregar", command=lambda: self.show("add"), width=12)
            self.btn_search = tk.Button(btn_frame, text="Busqueda", command=lambda: self.show("search"), width=12)
            self.btn_modify = tk.Button(btn_frame, text="Modificacion", command=lambda: self.show("modify"), width=12)

            self.btn_add.grid(row=0, column=0, padx=8)
            self.btn_search.grid(row=0, column=1, padx=8)
            self.btn_modify.grid(row=0, column=2, padx=8)

            # Frames container
            container = tk.Frame(self)
            container.pack(fill="both", expand=True, padx=8, pady=8)

            # --- Frames con controllers ---
            self.frames = {}
            self.frames["add"] = AddPersonFrame(
                container,
                controller=self.controller,
                config_service=self.config_controller
            )
            self.frames["search"] = SearchPersonFrame(
                container,
                controller=self.controller,
                config_service=self.config_controller,
            )
            self.frames["modify"] = ModifyPersonFrame(
                container,
                controller=self.controller,
                config_service=self.config_controller,
                on_data_changed=lambda: self.frames["search"]._on_search()
            )
            self.frames["config"] = ConfigurationFrame(
                container,
                config_service=self.config_controller
            )

            # Register refresh callbacks with config frame
            add_frame = self.frames.get("add")
            modify_frame = self.frames.get("modify")
            search_frame = self.frames.get("search")
            config_frame = self.frames.get("config")
            if add_frame and config_frame:
                config_frame._register_refresh_callback(add_frame.refresh_dropdowns)
            if modify_frame and config_frame:
                config_frame._register_refresh_callback(modify_frame.refresh_dropdowns)
            if search_frame and config_frame:
                config_frame._register_refresh_callback(search_frame.refresh_dropdowns)

            # Wire the search frame so it can open the modify frame directly
            try:
                search_frame = self.frames.get("search")
                modify_frame = self.frames.get("modify")
                if search_frame is not None:
                    search_frame._open_modify_cb = self._open_modify
            except Exception:
                pass

            # Place all frames
            for f in self.frames.values():
                f.place(relx=0, rely=0, relwidth=1, relheight=1)

            self.show("add")

        def _open_modify(self, person_id: int, show: bool = False):
            """Populate modify frame with person_id and show it if requested."""
            mod = self.frames.get("modify")
            if not mod:
                return
            try:
                mod.load_person_by_id(person_id)
            except Exception:
                pass
            if show:
                self.show("modify")

        def show(self, key: str):
            for k, f in self.frames.items():
                if k == key:
                    f.lift()
                else:
                    f.lower()

    return MainWindow(app)


def run_frontend():
    app = create_app()
    wnd = _build_main_window(app)
    wnd.mainloop()


if __name__ == "__main__":
    run_frontend()
