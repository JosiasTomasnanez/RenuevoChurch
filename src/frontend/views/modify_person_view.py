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
            row=len(fields) + 1, column=0, columnspan=2, pady=10
        )

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
            person = self.controller.get_person_by_id(int(pid))
            if not person:
                messagebox.showerror("Error", "Persona no encontrada")
                return

            self.person_id = person.person_id

            for key, entry in self.entries.items():
                if key == "person_id":
                    continue
                if hasattr(person, key) and getattr(person, key) is not None:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(getattr(person, key)))

            if hasattr(person, "baptized") and person.baptized:
                self.combos["baptized"].set("Sí")
            else:
                self.combos["baptized"].set("No")

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


        cdb_idx = self.combos["cdb"].current()
        if cdb_idx >= 0:
            payload["cdb_id"] = self._cdb_options[cdb_idx]["cdb_id"]

        payload["baptized"] = self.combos["baptized"].get() == "Sí"

        try:
            self.controller.update_person(self.person_id, payload)
            messagebox.showinfo("OK", "Persona actualizada")
        except Exception as e:
            messagebox.showerror("Error", str(e))
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