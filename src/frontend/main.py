from __future__ import annotations

import tkinter as tk

from src.frontend.api.people_api import PeopleAPI
from src.frontend.api.config_api import ConfigAPI

from src.frontend.views.person_view import (
    AddPersonFrame,
    SearchPersonFrame,
    ModifyPersonFrame,
)

from src.frontend.views.config_view import ConfigurationFrame


def _build_main_window():
    """Create and return a configured Tk main window instance."""

    class MainWindow(tk.Tk):

        def __init__(self):
            super().__init__()

            self.title("Renuevo — Administración")

            # maximize window cross-platform
            try:
                self.state("zoomed")
            except Exception:
                self.attributes("-zoomed", True)

            # API clients
            self.people_api = PeopleAPI()
            self.config_api = ConfigAPI()

            self._build_ui()

        def _build_ui(self):

            top = tk.Frame(self)
            top.pack(side="top", fill="x", pady=8)

            # configuration button
            self.btn_config = tk.Button(
                top,
                text="Configurar",
                command=lambda: self.show("config"),
                width=12,
                fg="darkblue",
            )
            self.btn_config.pack(side="left", padx=8)

            # centered buttons
            btn_frame = tk.Frame(top)
            btn_frame.pack(anchor="n", expand=True)

            self.btn_add = tk.Button(
                btn_frame,
                text="Agregar",
                command=lambda: self.show("add"),
                width=12,
            )

            self.btn_search = tk.Button(
                btn_frame,
                text="Busqueda",
                command=lambda: self.show("search"),
                width=12,
            )

            self.btn_modify = tk.Button(
                btn_frame,
                text="Modificacion",
                command=lambda: self.show("modify"),
                width=12,
            )

            self.btn_add.grid(row=0, column=0, padx=8)
            self.btn_search.grid(row=0, column=1, padx=8)
            self.btn_modify.grid(row=0, column=2, padx=8)

            # container for frames
            container = tk.Frame(self)
            container.pack(fill="both", expand=True, padx=8, pady=8)

            self.frames = {}

            # Frames using API clients
            self.frames["add"] = AddPersonFrame(
                container,
                controller=self.people_api,
                config_service=self.config_api,
            )

            self.frames["search"] = SearchPersonFrame(
                container,
                controller=self.people_api,
                config_service=self.config_api,
            )

            self.frames["modify"] = ModifyPersonFrame(
                container,
                controller=self.people_api,
                config_service=self.config_api,
                on_data_changed=lambda: self.frames["search"]._on_search(),
            )

            self.frames["config"] = ConfigurationFrame(
                container,
                config_service=self.config_api,
            )

            # register refresh callbacks
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

            # allow search → open modify
            try:
                if search_frame:
                    search_frame._open_modify_cb = self._open_modify
            except Exception:
                pass

            # place frames
            for frame in self.frames.values():
                frame.place(relx=0, rely=0, relwidth=1, relheight=1)

            self.show("add")

        def _open_modify(self, person_id: int, show: bool = False):

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

            for name, frame in self.frames.items():

                if name == key:
                    frame.lift()
                else:
                    frame.lower()

    return MainWindow()


def run_frontend():
    wnd = _build_main_window()
    wnd.mainloop()


if __name__ == "__main__":
    run_frontend()