"""Tkinter front-end entrypoint for the MVC app.

This module builds a small Tkinter UI with three frames (Agregar, Busqueda,
Modificacion) and three centered top buttons to switch between them.

It uses the backend app factory to obtain `db` and `services` and then
creates a `PersonController` from the frontend controller module.
"""
from __future__ import annotations

from src.backend.app.main import create_app
from src.frontend.controllers.person_controller import get_controller
from src.frontend.views.person_view import AddPersonFrame, SearchPersonFrame, ModifyPersonFrame


def _build_main_window(app):
	"""Create and return a configured Tk main window instance.

	This helper imports tkinter lazily to avoid requiring the GUI on import
	time so tests and other tools can import frontend modules safely.
	"""
	import tkinter as tk

	class MainWindow(tk.Tk):
		def __init__(self, app):
			super().__init__()
			self.title("Renuevo — Administración")
			self.geometry("900x600")

			self.app = app
			self.controller = get_controller(app.db, app.services)

			self._build_ui()

		def _build_ui(self):
			# top button bar, centered
			top = tk.Frame(self)
			top.pack(side="top", fill="x", pady=8)

			btn_frame = tk.Frame(top)
			btn_frame.pack(anchor="n")

			self.btn_add = tk.Button(btn_frame, text="Agregar", command=lambda: self.show("add"), width=12)
			self.btn_search = tk.Button(btn_frame, text="Busqueda", command=lambda: self.show("search"), width=12)
			self.btn_modify = tk.Button(btn_frame, text="Modificacion", command=lambda: self.show("modify"), width=12)

			# set them centered using grid
			self.btn_add.grid(row=0, column=0, padx=8)
			self.btn_search.grid(row=0, column=1, padx=8)
			self.btn_modify.grid(row=0, column=2, padx=8)

			# frames container
			container = tk.Frame(self)
			container.pack(fill="both", expand=True, padx=8, pady=8)

			self.frames = {}
			self.frames["add"] = AddPersonFrame(container, controller=self.controller)
			self.frames["search"] = SearchPersonFrame(container, controller=self.controller)
			self.frames["modify"] = ModifyPersonFrame(container, controller=self.controller)

			# wire the search frame so it can open the modify frame directly
			try:
				search_frame = self.frames.get("search")
				if search_frame is not None:
					search_frame._open_modify_cb = self._open_modify
			except Exception:
				# be permissive if the widget doesn't expose expected internals
				pass

			for f in self.frames.values():
				f.place(relx=0, rely=0, relwidth=1, relheight=1)

			self.show("add")

		def _open_modify(self, person_id: int, show: bool = False):
			"""Helper: populate modify frame with person_id and show it."""
			mod = self.frames.get("modify")
			if not mod:
				return
			try:
				# populate the person id input and call the load handler
				mod.id_entry.delete(0, "end")
				mod.id_entry.insert(0, str(person_id))
				mod._on_load()
			except Exception:
				pass

			# show the modify screen only when explicitly requested
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
	# create the backend app (db + services) and create the GUI lazily
	app = create_app()  # uses default config and data/renuevo.db
	wnd = _build_main_window(app)
	wnd.mainloop()


if __name__ == "__main__":
	run_frontend()


