"""Tkinter views for person-related screens.

This module defines three frames:
 - AddPersonFrame: form to add a new person
 - SearchPersonFrame: search by neighborhood and show results in a table
 - ModifyPersonFrame: load a person by id and edit fields

Each frame is small and uses a supplied controller object for actions.
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


class AddPersonFrame(BaseFrame):
	def __init__(self, master, controller, open_modify_callback=None, **kwargs):
		if tk is None:
			raise RuntimeError("Tkinter not available in this environment — run GUI on a machine with Tk installed")
		super().__init__(master, **kwargs)
		self.controller = controller
		# callback(person_id) used to activate the Modify frame with the
		# selected person. Main window will pass it when creating the frame.
		self._open_modify_cb = open_modify_callback
		self._build()

	def _build(self):
		self.entries = {}
		fields = [
			("first_name", "Nombre"),
			("last_name", "Apellido"),
			("email", "Correo"),
			("dni", "DNI"),
			("phone_number", "Teléfono"),
			("street", "Calle"),
			("neighborhood", "Barrio"),
			("house_number", "Número"),
		]

		for i, (key, label) in enumerate(fields):
			tk.Label(self, text=label).grid(row=i, column=0, sticky="w", padx=6, pady=3)
			ent = tk.Entry(self, width=40)
			ent.grid(row=i, column=1, sticky="w", padx=6, pady=3)
			self.entries[key] = ent

		btn = tk.Button(self, text="Agregar", command=self._on_submit)
		btn.grid(row=len(fields), column=0, columnspan=2, pady=(10, 0))

	def _on_submit(self):
		payload = {k: (v.get() or None) for k, v in self.entries.items()}
		# Convert numeric fields
		if payload.get("dni"):
			try:
				payload["dni"] = int(payload["dni"])
			except Exception:
				messagebox.showerror("Error", "DNI must be a number")
				return
		if payload.get("house_number"):
			try:
				payload["house_number"] = int(payload["house_number"])
			except Exception:
				messagebox.showerror("Error", "House # must be a number")
				return

		try:
			person_id = self.controller.add_person(payload)
			messagebox.showinfo("OK", f"Persona creada con id={person_id}")
			for e in self.entries.values():
				e.delete(0, "end")
		except Exception as exc:
			messagebox.showerror("Error", str(exc))


class SearchPersonFrame(BaseFrame):
	def __init__(self, master, controller, open_modify_callback=None, **kwargs):
		if tk is None:
			raise RuntimeError("Tkinter not available in this environment — run GUI on a machine with Tk installed")
		# remove our custom callback from kwargs before handing to tk.Frame
		super().__init__(master, **{k: v for k, v in kwargs.items() if k != 'open_modify_callback'})
		self.controller = controller
		self._open_modify_cb = open_modify_callback
		self._build()

	def _build(self):
		top = tk.Frame(self)
		top.pack(fill="x", padx=6, pady=6)
		tk.Label(top, text="Buscar por nombre o apellido:").pack(side="left")
		self.search_entry = tk.Entry(top)
		self.search_entry.pack(side="left", padx=6)
		tk.Button(top, text="Buscar", command=self._on_search).pack(side="left")

		# results table
		cols = ("person_id", "first_name", "last_name", "email", "dni", "phone_number", "neighborhood")
		self.tree = ttk.Treeview(self, columns=cols, show="headings")
		# Friendly Spanish headers for the user-facing table
		headers = {
			"person_id": "ID",
			"first_name": "Nombre",
			"last_name": "Apellido",
			"email": "Correo",
			"dni": "DNI",
			"phone_number": "Teléfono",
			"neighborhood": "Barrio",
		}

		for c in cols:
			self.tree.heading(c, text=headers.get(c, c))
			self.tree.column(c, width=120, anchor="w")

		self.tree.pack(fill="both", expand=True, padx=6, pady=6)

		# allow double-click to open modify and clicks on the action column
		self.tree.bind("<Double-1>", self._on_modify_selected)
		self.tree.bind("<ButtonRelease-1>", self._maybe_action_click)

		# load all people initially
		self._on_search()

	def _on_search(self):
		q = self.search_entry.get().strip()
		results = self.controller.search(q)
		for row in self.tree.get_children():
			self.tree.delete(row)

		for r in results:
			# support either repository-style dict rows or service-style Person objects
			if isinstance(r, dict):
				person = r.get("person", {})
				address = r.get("address") or {}
				values = (
					person.get("person_id"),
					person.get("first_name"),
					person.get("last_name"),
					person.get("email"),
					person.get("dni"),
					person.get("phone_number"),
					address.get("neighborhood"),
				)
			else:
				# assume Person dataclass-like object
				addr = getattr(r, "address", None)
				values = (
					getattr(r, "person_id", None),
					getattr(r, "first_name", None),
					getattr(r, "last_name", None),
					getattr(r, "email", None),
					getattr(r, "dni", None),
					getattr(r, "phone_number", None),
					getattr(addr, "neighborhood", None) if addr is not None else None,
				)

			values = tuple(values)
			self.tree.insert("", "end", values=values)

	def _on_modify_selected(self, event=None):
		"""Load the currently selected row into the Modify form.

		If the call comes from a double-click event the row under the
		cursor will be selected first so the user doesn't have to click
		before double-clicking.
		"""
		# If nothing is currently selected, use the event y coordinate
		# to identify the row under the pointer and select it.
		sel = self.tree.selection()
		if (not sel) and (event is not None):
			rowid = self.tree.identify_row(event.y)
			if rowid:
				self.tree.selection_set(rowid)
				sel = (rowid,)

		if not sel:
			return
		item = sel[0]
		values = self.tree.item(item, "values")
		if not values:
			return
		try:
			pid = int(values[0])
		except Exception:
			return

		if self._open_modify_cb:
			# load into modify frame but do not show it (only load)
			self._open_modify_cb(pid, show=False)
		# If nothing is currently selected, figure out which row the
		# user double-clicked (use the event y coordinate) and select it.
		if not sel and event is not None:
			rowid = self.tree.identify_row(event.y)
			if rowid:
				self.tree.selection_set(rowid)
				sel = (rowid,)

	# clicking in table cells no longer triggers actions — we rely on
	# double-click to load the modify form. Keep a no-op method here in case
	# old code references it.
	def _maybe_action_click(self, event):
		return


class ModifyPersonFrame(BaseFrame):
	def __init__(self, master, controller, on_deleted_callback: Optional[callable] = None, **kwargs):
		if tk is None:
			raise RuntimeError("Tkinter not available in this environment — run GUI on a machine with Tk installed")
		super().__init__(master, **kwargs)
		self.controller = controller
		# optional callback to notify parent that a deletion happened
		# This callback should be a callable taking no arguments.
		self._on_deleted_cb = on_deleted_callback
		self._build()

	def _build(self):
		top = tk.Frame(self)
		top.pack(fill="x", padx=6, pady=6)
		tk.Label(top, text="Person ID:").pack(side="left")
		self.id_entry = tk.Entry(top, width=8)
		self.id_entry.pack(side="left", padx=6)
		tk.Button(top, text="Cargar", command=self._on_load).pack(side="left")

		self.form = {}
		fields = [
			("first_name", "Nombre"),
			("last_name", "Apellido"),
			("email", "Correo"),
			("dni", "DNI"),
			("phone_number", "Teléfono"),
			("street", "Calle"),
			("neighborhood", "Barrio"),
			("house_number", "Número"),
		]

		frm = tk.Frame(self)
		frm.pack(fill="both", expand=True, padx=6, pady=6)
		for i, (key, label) in enumerate(fields):
			tk.Label(frm, text=label).grid(row=i, column=0, sticky="w", padx=6, pady=3)
			ent = tk.Entry(frm, width=40)
			ent.grid(row=i, column=1, sticky="w", padx=6, pady=3)
			self.form[key] = ent

		# Buttons: Save and Delete side-by-side
		btn_save = tk.Button(frm, text="Guardar cambios", command=self._on_save)
		btn_save.grid(row=len(fields), column=0, sticky="e", padx=(0, 6), pady=(10, 0))

		btn_delete = tk.Button(frm, text="Eliminar", fg="white", bg="#c0392b", command=self._on_delete)
		btn_delete.grid(row=len(fields), column=1, sticky="w", pady=(10, 0))


	def _on_load(self):
		pid = self.id_entry.get().strip()
		if not pid:
			messagebox.showerror("Error", "Ingrese person_id")
			return
		try:
			pid = int(pid)
		except Exception:
			messagebox.showerror("Error", "person_id debe ser numerico")
			return

		person = self.controller.get_person(pid)
		if not person:
			messagebox.showinfo("No encontrado", "No se encontro la persona")
			return

		# populate
		self.form["first_name"].delete(0, "end"); self.form["first_name"].insert(0, person.first_name or "")
		self.form["last_name"].delete(0, "end"); self.form["last_name"].insert(0, person.last_name or "")
		self.form["email"].delete(0, "end"); self.form["email"].insert(0, person.email or "")
		self.form["dni"].delete(0, "end"); self.form["dni"].insert(0, person.dni or "")
		self.form["phone_number"].delete(0, "end"); self.form["phone_number"].insert(0, person.phone_number or "")
		# address
		if person.address:
			self.form["street"].delete(0, "end"); self.form["street"].insert(0, person.address.street or "")
			self.form["neighborhood"].delete(0, "end"); self.form["neighborhood"].insert(0, person.address.neighborhood or "")
			self.form["house_number"].delete(0, "end"); self.form["house_number"].insert(0, person.address.house_number or "")
		else:
			self.form["street"].delete(0, "end")
			self.form["neighborhood"].delete(0, "end")
			self.form["house_number"].delete(0, "end")

	def _on_save(self):
		pid = self.id_entry.get().strip()
		if not pid:
			messagebox.showerror("Error", "Carga un person_id primero")
			return
		try:
			pid = int(pid)
		except Exception:
			messagebox.showerror("Error", "person_id debe ser numerico")
			return

		payload = {k: (v.get() or None) for k, v in self.form.items()}
		if payload.get("dni"):
			try:
				payload["dni"] = int(payload["dni"])
			except Exception:
				messagebox.showerror("Error", "DNI must be a number")
				return
		if payload.get("house_number"):
			try:
				payload["house_number"] = int(payload["house_number"])
			except Exception:
				messagebox.showerror("Error", "House # must be a number")
				return

		ok = self.controller.update_person(pid, payload)
		if ok:
			messagebox.showinfo("OK", "Actualizado")
		else:
			messagebox.showerror("Error", "No se pudo actualizar")

	def _on_delete(self):
		pid = self.id_entry.get().strip()
		if not pid:
			messagebox.showerror("Error", "Carga un person_id primero")
			return
		try:
			pid_int = int(pid)
		except Exception:
			messagebox.showerror("Error", "person_id debe ser numerico")
			return

		ok = messagebox.askyesno("Confirmar eliminación", "¿Está seguro que desea eliminar esta persona? Esta acción es irreversible.")
		if not ok:
			return

		try:
			res = self.controller.delete_person(pid_int)
		except Exception as exc:
			messagebox.showerror("Error", str(exc))
			return

		if res:
			messagebox.showinfo("Eliminado", "Persona eliminada satisfactoriamente")
			# clear form fields and id
			self.id_entry.delete(0, "end")
			for ent in self.form.values():
				ent.delete(0, "end")
			# notify parent/UI that a deletion happened so e.g. search list can refresh
			try:
				if getattr(self, "_on_deleted_cb", None):
					self._on_deleted_cb()
			except Exception:
				# swallow errors in UI callback
				pass
		else:
			messagebox.showerror("Error", "No se pudo eliminar la persona")


__all__ = ["AddPersonFrame", "SearchPersonFrame", "ModifyPersonFrame"]


