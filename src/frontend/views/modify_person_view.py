import tkinter as tk
from tkinter import ttk, messagebox


class ModifyPersonFrame(tk.Frame):
    def __init__(self, parent, controller=None, config_service=None):
        super().__init__(parent)

        self.controller = controller
        self.config_service = config_service

        self.entries = {}
        self.combos = {}
        self.person_id = None

        self._ministry_options = []
        self._area_options = []

        self._build()

    # ---------------- UI ----------------

    def _build(self):
        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=10, fill="x")

        fields = [
            ("person_id", "ID Persona"),
            ("first_name", "Nombre"),
            ("last_name", "Apellido"),
            ("email", "Correo"),
            ("birthdate", "Fecha de nacimiento (YYYY-MM-DD)"),
            ("dni", "DNI"),
            ("phone_number", "Teléfono"),
            ("marital_status", "Estado civil"),
            ("social_security", "Número de seguro social"),
            ("street", "Calle"),
            ("neighborhood", "Barrio"),
            ("house_number", "Número de casa"),
            ("ministry_id", "Ministerio"),
            ("area_id", "Área"),
            ("consolidation_id", "Nivel de consolidación"),
            ("cdb", "¿CDB?"),
            ("baptized", "¿Bautizado?"),
        ]

        for i, (key, label) in enumerate(fields):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky="e", padx=6, pady=3)

            if key == "person_id":
                e = ttk.Entry(frm, width=40)
                e.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = e

                ttk.Button(frm, text="Cargar", command=self._on_load).grid(
                    row=i, column=2, padx=4
                )

            elif key == "ministry_id":
                combo = ttk.Combobox(frm, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                combo.bind("<<ComboboxSelected>>", self._on_ministry_selected)
                self.combos[key] = combo
                self._refresh_ministry_combo()

            elif key == "area_id":
                combo = ttk.Combobox(frm, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo

            elif key == "consolidation_id":
                combo = ttk.Combobox(frm, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
                self._refresh_consolidation_combo()

            elif key == "cdb":
                combo = ttk.Combobox(frm, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
                self._refresh_cdb_combo()


            elif key == "baptized":
                combo = ttk.Combobox(frm, width=37, state="readonly")
                combo["values"] = ["Sí", "No"]
                combo.current(1)
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo

            else:
                e = ttk.Entry(frm, width=40)
                e.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = e

        ttk.Button(frm, text="Guardar cambios", command=self._on_save).grid(
            row=len(fields) + 1, column=0, pady=10, padx=5, sticky="e"
        )

        ttk.Button(
            frm,
            text="Eliminar persona",
            command=self._on_delete,
        ).grid(row=len(fields) + 1, column=1, pady=10, padx=5, sticky="w")

    # ---------------- Config helpers ----------------

    def _refresh_ministry_combo(self):
        if not self.config_service:
            return
        try:
            ministries = self.config_service.get_all_ministries()
            self._ministry_options = ministries
            names = [m["name"] for m in ministries]
            self.combos["ministry_id"]["values"] = names
        except Exception:
            pass

    def _on_ministry_selected(self, event=None):
        idx = self.combos["ministry_id"].current()
        if idx < 0:
            return

        ministry_id = self._ministry_options[idx]["ministry_id"]

        try:
            areas = self.config_service.get_areas_by_ministry(ministry_id)
            self._area_options = areas
            labels = [a["area"] for a in areas]
            self.combos["area_id"]["values"] = labels
            self.combos["area_id"].set("")
        except Exception:
            pass

    # ---------------- Load person ----------------

    def _on_load(self):
        pid = self.entries["person_id"].get().strip()

        if not pid:
            messagebox.showerror("Error", "Ingresá un ID")
            return

        try:
            person = self.controller.get_person(int(pid))
            if not person:
                messagebox.showerror("Error", "Persona no encontrada")
                return

        # limpiar formulario antes de cargar nuevos datos
            self._clear_form()

            self.person_id = person.person_id
            self.entries["person_id"].insert(0, str(person.person_id))

            for key, entry in self.entries.items():
                if key == "person_id":
                    continue

                if hasattr(person, key) and getattr(person, key) is not None:
                    entry.insert(0, str(getattr(person, key)))

            if hasattr(person, "baptized") and person.baptized:
                self.combos["baptized"].set("Sí")
            else:
                self.combos["baptized"].set("No")

            # Load ministry and area if the person has them assigned
            if hasattr(person, "ministry_area_id") and person.ministry_area_id:
                try:
                    area_info = self.controller.services.people.get_area_and_ministry_service(person.ministry_area_id)
                    if area_info:
                        area_data = area_info.get("area")
                        ministry_data = area_info.get("ministry")
                        
                        if ministry_data:
                            ministry_id = ministry_data.get("ministry_id")
                            # Find and select the ministry in the combo
                            for idx, m in enumerate(self._ministry_options):
                                if m["ministry_id"] == ministry_id:
                                    self.combos["ministry_id"].current(idx)
                                    # Load areas for this ministry
                                    try:
                                        areas = self.config_service.get_areas_by_ministry(ministry_id)
                                        self._area_options = areas
                                        labels = [a["area"] for a in areas]
                                        self.combos["area_id"]["values"] = labels
                                        # Select the current area
                                        if area_data:
                                            current_area_id = area_data.get("area_id")
                                            for area_idx, a in enumerate(areas):
                                                if a["area_id"] == current_area_id:
                                                    self.combos["area_id"].current(area_idx)
                                                    break
                                    except Exception:
                                        pass
                                    break
                except Exception:
                    pass

        except Exception as e:
            messagebox.showerror("Error", str(e))


    # ---------------- Save ----------------

    def _on_save(self):
        if not self.person_id:
            messagebox.showerror("Error", "Primero cargá una persona")
            return

        payload = {}

        for key, entry in self.entries.items():
            if key == "person_id":
                continue
            payload[key] = entry.get()

        if "consolidation_id" in self.combos:
            idx = self.combos["consolidation_id"].current()
            if idx >= 0:
                payload["consolidation_id"] = self._consolidation_options[idx]["consolidation_id"]

        # ministry and area
        min_idx = self.combos["ministry_id"].current()
        selected_ministry_id = None
        if min_idx >= 0 and hasattr(self, "_ministry_options"):
            selected_ministry_id = self._ministry_options[min_idx]["ministry_id"]

        area_idx = self.combos["area_id"].current()
        
        # If area is selected, use ministry_area_id (which links to ministry through the area)
        if area_idx >= 0 and hasattr(self, "_area_options"):
            payload["ministry_area_id"] = self._area_options[area_idx]["area_id"]
            # ministry_id gets set from the area, not directly
            payload["ministry_id"] = None
        else:
            # No area selected, so use ministry_id directly if ministry is selected
            payload["ministry_area_id"] = None
            if selected_ministry_id is not None:
                payload["ministry_id"] = selected_ministry_id
            else:
                payload["ministry_id"] = None

        cdb_idx = self.combos["cdb"].current()
        if cdb_idx >= 0:
            payload["cdb_id"] = self._cdb_options[cdb_idx]["cdb_id"]

        payload["baptized"] = self.combos["baptized"].get() == "Sí"

        try:
            self.controller.update_person(self.person_id, payload)
            messagebox.showinfo("OK", "Persona actualizada")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_delete(self):
        if not self.person_id:
            messagebox.showerror("Error", "Primero cargá una persona")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar esta persona?"):
            return

        try:
            self.controller.delete_person(self.person_id)
            messagebox.showinfo("OK", "Persona eliminada")

        # limpiar formulario
            for entry in self.entries.values():
                entry.delete(0, tk.END)

            for combo in self.combos.values():
                combo.set("")

            self.person_id = None

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

        for combo in self.combos.values():
            combo.set("")

        # valor por defecto para bautizado
        if "baptized" in self.combos:
            self.combos["baptized"].set("No")

    def load_person_by_id(self, person_id: int):
        """Public method used by Search frame to load a person."""
        self.entries["person_id"].delete(0, tk.END)
        self.entries["person_id"].insert(0, str(person_id))
        self._on_load()

    def refresh_dropdowns(self):
        self._refresh_ministry_combo()
        self._refresh_consolidation_combo()
        self._refresh_cdb_combo()

        if "area_id" in self.combos:
            self.combos["area_id"]["values"] = []
            self.combos["area_id"].set("")


    def _refresh_consolidation_combo(self):
        if not self.config_service:
            return
        try:
            consolidations = self.config_service.get_all_consolidations()
            self._consolidation_options = consolidations
            labels = [c["level"] for c in consolidations]
            self.combos["consolidation_id"]["values"] = labels
        except Exception:
            pass


    def _refresh_cdb_combo(self):
        if not self.config_service:
            return
        try:
            cdbs = self.config_service.get_all_cdb_options()
            self._cdb_options = cdbs
            labels = [str(c["number"]) for c in cdbs]
            self.combos["cdb"]["values"] = labels
        except Exception:
            pass