import tkinter as tk
from tkinter import ttk, messagebox
from src.frontend.views._base import BaseFrame


class ModifyPersonFrame(BaseFrame):
    # Pastel color scheme
    BG_PRIMARY = "#F0E6F6"      # Light purple
    BG_INPUT = "#FFFBF5"        # Warm white
    BTN_COLOR = "#7A4A97"       # Strong dark purple
    TEXT_DARK = "#5A5A5A"       # Dark gray for text
    
    def __init__(self, parent, controller=None, config_service=None, on_data_changed=None):

        super().__init__(parent)
        self.config(bg=self.BG_PRIMARY)

        self.controller = controller
        self.config_service = config_service
        self._on_data_changed = on_data_changed


        self.entries = {}
        self.combos = {}
        self.person_id = None

        self._ministry_options = []
        self._area_options = []
        self._consolidation_options = []
        self._cdb_options = []

        self._build()

    # ---------------- UI ----------------

    def _build(self):
        main = tk.Frame(self, bg=self.BG_PRIMARY)
        main.pack(padx=10, pady=10, fill="both", expand=True)

        # columna izquierda (datos)
        left = tk.Frame(main, bg=self.BG_PRIMARY)
        left.pack(side="left", fill="both", expand=True)

        # columna derecha (ministerios)
        right = tk.Frame(main, bg=self.BG_PRIMARY)
        right.pack(side="right", fill="y", padx=(20, 0))
        frm = left

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
            # Ministry/area assignments handled by dedicated editor below
            ("consolidation_id", "Nivel de consolidación"),
            ("cdb", "¿CDB?"),
            ("baptized", "¿Bautizado?"),
        ]

        for i, (key, label) in enumerate(fields):
            lbl = tk.Label(frm, text=label, bg=self.BG_PRIMARY, fg=self.TEXT_DARK)
            lbl.grid(row=i, column=0, sticky="w", padx=6, pady=3)

            if key == "person_id":
                e = tk.Entry(frm, width=40, bg=self.BG_INPUT, fg=self.TEXT_DARK, relief="solid", bd=1)
                e.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = e

                load_btn = tk.Button(frm, text="Cargar", command=self._on_load, bg=self.BTN_COLOR, fg="white", relief="raised", bd=1, activebackground="#5A2A77")
                load_btn.grid(row=i, column=2, padx=4)

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
                e = tk.Entry(frm, width=40, bg=self.BG_INPUT, fg=self.TEXT_DARK, relief="solid", bd=1)
                e.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = e

       # Membership editor (igual que AddPersonFrame)
        lbl = tk.Label(right, text="Asignaciones (ministerio / área)", bg=self.BG_PRIMARY, fg=self.TEXT_DARK)
        lbl.grid(row=0, column=0, sticky="nw", padx=6, pady=(0, 3))

        mem_frame = tk.Frame(right, bg=self.BG_PRIMARY)
        mem_frame.grid(row=1, column=0, sticky="nwe", padx=6, pady=(0, 3))

        self._membership_frame = mem_frame

        self._mem_ministry_combo = ttk.Combobox(mem_frame, width=20, state="readonly")
        self._mem_area_combo = ttk.Combobox(mem_frame, width=20, state="readonly")

        self._mem_ministry_combo.grid(row=0, column=0, padx=(0, 4), pady=2, sticky="w")
        self._mem_area_combo.grid(row=0, column=1, padx=(0, 4), pady=2, sticky="w")

        self._mem_ministry_combo.bind("<<ComboboxSelected>>", self._on_ministry_selected)

        tk.Button(
            mem_frame,
            text="Agregar asignación",
            command=self._on_add_membership,
            bg=self.BTN_COLOR,
            fg="white",
            relief="raised",
            bd=1,
            activebackground="#5A2A77",
        ).grid(row=0, column=3, padx=(0, 4), pady=2, sticky="w")

        self._membership_list = tk.Listbox(
            mem_frame,
            height=4,
            bg=self.BG_INPUT,
            fg=self.TEXT_DARK,
            relief="solid",
            bd=1,
        )
        self._membership_list.grid(row=1, column=0, columnspan=3, sticky="we", pady=(4, 0))

        tk.Button(
            mem_frame,
            text="Quitar seleccionada",
            command=self._on_remove_membership,
            bg="#A83030",
            fg="white",
            relief="raised",
            bd=1,
            activebackground="#8A1010",
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(4, 0))

        mem_frame.columnconfigure(0, weight=1)
        # Internal memberships list
        self._memberships = []

        # Initialize combos for membership editor
        self._refresh_ministry_combo()

        save_btn = tk.Button(frm, text="Guardar cambios", command=self._on_save, bg=self.BTN_COLOR, fg="white", relief="raised", bd=1, activebackground="#5A2A77")
        save_btn.grid(row=len(fields) + 1, column=0, pady=10, padx=5, sticky="e")

        delete_btn = tk.Button(frm, text="Eliminar persona", command=self._on_delete, bg="#A83030", fg="white", relief="raised", bd=1, activebackground="#8A1010")
        delete_btn.grid(row=len(fields) + 1, column=1, pady=10, padx=5, sticky="w")

    # ---------------- Config helpers ----------------

    def _refresh_ministry_combo(self):
        if not self.config_service:
            return
        try:
            ministries = self.config_service.get_all_ministries()
            self._ministry_options = ministries
            names = [m["name"] for m in ministries]
            self._mem_ministry_combo["values"] = names
        except Exception:
            pass

    def _on_ministry_selected(self, event=None):
        idx = self._mem_ministry_combo.current()
        if idx < 0:
            return

        ministry_id = self._ministry_options[idx]["ministry_id"]

        try:
            areas = self.config_service.get_areas_by_ministry(ministry_id)
            self._area_options = areas
            labels = [a["area"] for a in areas]
            self._mem_area_combo["values"] = labels
            self._mem_area_combo.set("")
        except Exception:
            pass

    # ---------------- Helper loaders (refactor _on_load) ----------------

    def _fetch_person(self, pid):
        try:
            return self.controller.get_person(int(pid))
        except Exception:
            return None

    def _populate_basic_fields(self, person):
        # set id and simple fields + address nested fields
        self.person_id = person.person_id
        self.entries["person_id"].insert(0, str(person.person_id))

        for key, entry in self.entries.items():
            if key == "person_id":
                continue

            if hasattr(person, key) and getattr(person, key) is not None:
                entry.insert(0, str(getattr(person, key)))
            elif key in ("street", "neighborhood", "house_number"):
                addr = getattr(person, "address", None)
                if addr and hasattr(addr, key) and getattr(addr, key) is not None:
                    entry.insert(0, str(getattr(addr, key)))

    def _set_baptized(self, person):
        try:
            if hasattr(person, "baptized") and person.baptized:
                self.combos["baptized"].set("Sí")
            else:
                self.combos["baptized"].set("No")
        except Exception:
            pass

    def _load_ministry_and_area(self, person):
        # Load memberships for this person and populate the editor.
        self._memberships = []
        self._membership_list.delete(0, tk.END)

        try:
            if hasattr(self.controller, "get_memberships") and self.person_id is not None:
                raw_memberships = self.controller.get_memberships(self.person_id) or []
            else:
                raw_memberships = []
        except Exception:
            raw_memberships = []

        if not raw_memberships:
            return

        # Ensure ministry list is available for name resolution
        try:
            if not self._ministry_options:
                self._refresh_ministry_combo()
        except Exception:
            pass

        # Preload areas per ministry to speed up label building
        areas_cache = {}
        if self.config_service:
            try:
                for m in self._ministry_options:
                    mid = m.get("ministry_id")
                    if mid is not None and mid not in areas_cache:
                        areas_cache[mid] = self.config_service.get_areas_by_ministry(mid)
            except Exception:
                areas_cache = {}

        for rm in raw_memberships:
            ministry = rm.get("ministry") or {}
            area = rm.get("area") or {}
            ministry_id = ministry.get("ministry_id") or rm.get("ministry_id")
            area_id = area.get("area_id") or rm.get("area_id")

            ministry_name = ministry.get("name") or ""
            if not ministry_name and ministry_id is not None:
                for m in self._ministry_options:
                    if m.get("ministry_id") == ministry_id:
                        ministry_name = m.get("name") or ""
                        break

            area_name = area.get("area") or ""
            if not area_name and ministry_id is not None and area_id is not None:
                for a in areas_cache.get(ministry_id, []):
                    if a.get("area_id") == area_id:
                        area_name = a.get("area") or ""
                        break

            mem = {
                "ministry_id": ministry_id,
                "area_id": area_id,
                "ministry_name": ministry_name,
                "area_name": area_name,
            }
            self._memberships.append(mem)

        self._refresh_membership_listbox()

    def _select_consolidation(self, person):
        try:
            if hasattr(person, "consolidation_id") and person.consolidation_id is not None and "consolidation_id" in self.combos:
                self._refresh_consolidation_combo()
                for idx, c in enumerate(self._consolidation_options):
                    if c.get("consolidation_id") == person.consolidation_id:
                        self.combos["consolidation_id"].current(idx)
                        break
        except Exception:
            pass

    def _select_cdb(self, person):
        try:
            if hasattr(person, "cdb") and person.cdb is not None and "cdb" in self.combos:
                self._refresh_cdb_combo()
                for idx, c in enumerate(self._cdb_options):
                    if c.get("cdb_id") == person.cdb:
                        self.combos["cdb"].current(idx)
                        break
        except Exception:
            pass

    # ---------------- Load person ----------------

    def _on_load(self):
        pid = self.entries["person_id"].get().strip()

        if not pid:
            messagebox.showerror("Error", "Ingresá un ID")
            return

        person = self._fetch_person(pid)
        if not person:
            messagebox.showerror("Error", "Persona no encontrada")
            return

        # limpiar formulario antes de cargar nuevos datos
        self._clear_form()

        # populate fields and combos using helpers
        try:
            self._populate_basic_fields(person)
            self._set_baptized(person)
            self._load_ministry_and_area(person)
            self._select_consolidation(person)
            self._select_cdb(person)
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

        # Ministry assignments now live in person_ministry; keep legacy fields empty
        payload["ministry_area_id"] = None
        payload["ministry_id"] = None

        cdb_idx = self.combos["cdb"].current()
        if cdb_idx >= 0:
            # backend expects `cdb` field (stores cdb_id in person.cdb)
            payload["cdb"] = self._cdb_options[cdb_idx]["cdb_id"]

        payload["baptized"] = self.combos["baptized"].get() == "Sí"

        try:
            self.controller.update_person(self.person_id, payload)
            # Persist memberships via backend services
            try:
                services = getattr(self.controller, "services", None)
                if services is not None:
                    people_svc = getattr(services, "people", None)
                    if people_svc is not None and self._memberships:
                        updater = getattr(people_svc, "update_person_memberships", None)
                        if updater is not None:
                            db_memberships = [
                                {
                                    "ministry_id": m.get("ministry_id"),
                                    "area_id": m.get("area_id"),
                                }
                                for m in self._memberships
                            ]
                            updater(self.person_id, db_memberships)
            except Exception:
                pass
            messagebox.showinfo("OK", "Persona actualizada")
            if self._on_data_changed:
                self._on_data_changed()

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
            if self._on_data_changed:
                self._on_data_changed()


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

        # clear memberships list
        self._memberships = []
        self._membership_list.delete(0, tk.END)

    def load_person_by_id(self, person_id: int):
        """Public method used by Search frame to load a person."""
        self.entries["person_id"].delete(0, tk.END)
        self.entries["person_id"].insert(0, str(person_id))
        self._on_load()

    def refresh_dropdowns(self):
        self._refresh_ministry_combo()
        self._refresh_consolidation_combo()
        self._refresh_cdb_combo()

        self._mem_area_combo["values"] = []
        self._mem_area_combo.set("")

    def _on_add_membership(self):
        """Add a membership to the internal list and listbox."""
        if not self._ministry_options:
            self._refresh_ministry_combo()

        min_idx = self._mem_ministry_combo.current()
        if min_idx < 0 or min_idx >= len(self._ministry_options):
            messagebox.showerror("Error", "Seleccione un ministerio")
            return

        ministry = self._ministry_options[min_idx]
        ministry_id = ministry.get("ministry_id")
        ministry_name = ministry.get("name") or ""

        area_id = None
        area_name = ""
        area_idx = self._mem_area_combo.current()
        if self._area_options and 0 <= area_idx < len(self._area_options):
            area = self._area_options[area_idx]
            area_id = area.get("area_id")
            area_name = area.get("area") or ""

        mem = {
            "ministry_id": ministry_id,
            "area_id": area_id,
            "ministry_name": ministry_name,
            "area_name": area_name,
        }
        self._memberships.append(mem)

        self._refresh_membership_listbox()

    def _refresh_membership_listbox(self):
        if hasattr(self, "_membership_list"):
            self._membership_list.delete(0, tk.END)
        for m in self._memberships:
            label = m.get("ministry_name") or ""
            if m.get("area_name"):
                label = f"{label} / {m.get('area_name')}"
            self._membership_list.insert(tk.END, label)

    def _on_remove_membership(self):
        sel = self._membership_list.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(self._memberships):
            del self._memberships[idx]
            self._refresh_membership_listbox()


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