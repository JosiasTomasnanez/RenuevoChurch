from src.frontend.views._base import BaseFrame, tk, messagebox, ttk

class AddPersonFrame(BaseFrame):
    # Pastel color scheme
    BG_PRIMARY = "#F0E6F6"      # Light purple
    BG_INPUT = "#FFFBF5"        # Warm white
    BTN_COLOR = "#7A4A97"       # Strong dark purple
    TEXT_DARK = "#5A5A5A"       # Dark gray for text
    
    def __init__(self, master, controller, config_service=None, open_modify_callback=None, **kwargs):
        if tk is None:
            raise RuntimeError("Tkinter not available in this environment — run GUI on a machine with Tk installed")
        super().__init__(master, **kwargs)
        self.controller = controller
        self.config_service = config_service
        self._open_modify_cb = open_modify_callback
        self.config(bg=self.BG_PRIMARY)
        
        # Initialize option lists
        self._ministry_options = []
        self._area_options = []
        self._consolidation_options = []
        self._cdb_options = []
        
        self._build()
        

    def _build(self):
        self.entries = {}
        self.combos = {}

        # Main layout: left = datos básicos, right = asignaciones
        main = tk.Frame(self, bg=self.BG_PRIMARY)
        main.pack(fill="both", expand=True, padx=6, pady=6)

        left = tk.Frame(main, bg=self.BG_PRIMARY)
        left.grid(row=0, column=0, sticky="nw")

        right = tk.Frame(main, bg=self.BG_PRIMARY)
        right.grid(row=0, column=1, sticky="ne", padx=(20, 0))

        # All available fields from person, address, and boolean flags
        fields = [
            # Person fields
            ("first_name", "Nombre *"),
            ("last_name", "Apellido *"),
            ("email", "Correo"),
            ("birthdate", "Fecha de nacimiento (YYYY-MM-DD)"),
            ("dni", "DNI"),
            ("phone_number", "Teléfono"),
            ("marital_status", "Estado civil"),
            ("social_security", "Número de seguro social"),
            # Address fields
            ("street", "Calle"),
            ("neighborhood", "Barrio"),
            ("house_number", "Número de casa"),
            # Ministry/Area editor will be handled separately below
            # Consolidation level (dropdown)
            ("consolidation_id", "Nivel de consolidación"),
            # CDB (dropdown)
            ("cdb", "¿CDB?"),
            ("baptized", "¿Bautizado?"),
        ]

        for i, (key, label) in enumerate(fields):
            lbl = tk.Label(left, text=label, bg=self.BG_PRIMARY, fg=self.TEXT_DARK)
            lbl.grid(row=i, column=0, sticky="w", padx=6, pady=3)
            
            if key == "consolidation_id":
                # Dropdown for consolidation
                combo = ttk.Combobox(left, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
                self._refresh_consolidation_combo()
            elif key == "cdb":
                # Dropdown for CDB (house numbers)
                combo = ttk.Combobox(left, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
                self._refresh_cdb_combo()
            elif key == "baptized":
                combo = ttk.Combobox(left, width=37, state="readonly")
                combo["values"] = ["Sí", "No"]
                combo.current(1)  # default = No
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
            else:
                ent = tk.Entry(left, width=40, bg=self.BG_INPUT, fg=self.TEXT_DARK, relief="solid", bd=1)
                ent.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = ent

        # Button to create person (stays en la parte izquierda)
        btn = tk.Button(left, text="Agregar persona", command=self._on_submit, bg=self.BTN_COLOR, fg="white", relief="raised", bd=1, activebackground="#5A2A77")
        btn.grid(row=len(fields), column=0, columnspan=2, pady=(12, 0))

        # Membership editor (ministries/areas) en la mitad derecha
        lbl = tk.Label(right, text="Asignaciones (ministerio / área)", bg=self.BG_PRIMARY, fg=self.TEXT_DARK)
        lbl.grid(row=0, column=0, sticky="nw", padx=6, pady=(0, 3))

        mem_frame = tk.Frame(right, bg=self.BG_PRIMARY)
        mem_frame.grid(row=1, column=0, sticky="nwe", padx=6, pady=(0, 3))
        self._membership_frame = mem_frame

        # Controls to add a membership
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

        # List of current memberships
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

        # Internal list of memberships to send to backend
        self._memberships = []

        # Initialize combos for membership editor
        self._refresh_ministry_combo()
        self._refresh_area_combo()
    
    def _refresh_area_combo(self):
        """Reset area combo (values will be filled when a ministry is selected)."""
        self._area_options = []
        try:
            self._mem_area_combo["values"] = []
            self._mem_area_combo.set("")
        except Exception:
            pass
    
    def _refresh_consolidation_combo(self):
        """Load consolidation levels into the combo box."""
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
        """Load CDB options into the combo box."""
        if not self.config_service:
            return
        try:
            cdb_options = self.config_service.get_all_cdb_options()
            self._cdb_options = cdb_options
            labels = [str(cdb["number"]) for cdb in cdb_options]
            self.combos["cdb"]["values"] = labels
        except Exception:
            pass
    
    def refresh_dropdowns(self):
        """Refresh all dropdown lists (called when config changes)."""
        self._refresh_ministry_combo()
        self._refresh_area_combo()
        self._refresh_consolidation_combo()
        self._refresh_cdb_combo()

    
    def _refresh_ministry_combo(self):
        if not self.config_service:
            return
        try:
            ministries = self.config_service.get_all_ministries()
            self._ministry_options = ministries
            names = [m["name"] for m in ministries]
            # used by membership editor
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

    def _on_add_membership(self):
        """Add a membership row to the internal list and UI listbox."""
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

        # Refresh listbox
        self._refresh_membership_listbox()

    def _refresh_membership_listbox(self):
        self._membership_list.delete(0, "end")
        for m in self._memberships:
            label = m.get("ministry_name") or ""
            if m.get("area_name"):
                label = f"{label} / {m.get('area_name')}"
            self._membership_list.insert("end", label)

    def _on_remove_membership(self):
        sel = self._membership_list.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(self._memberships):
            del self._memberships[idx]
            self._refresh_membership_listbox()

    def _on_submit(self):

        # -------- build payload --------
        payload = {k: (v.get() or None) for k, v in self.entries.items()}

        # Required fields validation (avoid FastAPI 422)
        if not payload.get("first_name") or not payload.get("last_name"):
            messagebox.showerror("Error", "Nombre y Apellido son obligatorios")
            return

        # Ministry assignments are handled via memberships
        payload["ministry_area_id"] = None
        payload["ministry_id"] = None

        # -------- consolidation --------
        cons_idx = self.combos["consolidation_id"].current()
        if cons_idx >= 0 and hasattr(self, "_consolidation_options"):
            payload["consolidation_id"] = self._consolidation_options[cons_idx]["consolidation_id"]
        else:
            payload["consolidation_id"] = None

        # -------- cdb --------
        cdb_idx = self.combos["cdb"].current()
        if cdb_idx >= 0 and self._cdb_options:
            payload["cdb"] = self._cdb_options[cdb_idx]["cdb_id"]
        else:
            payload["cdb"] = None

        # -------- baptized --------
        payload["baptized"] = self.combos["baptized"].get() == "Sí"

        # -------- numeric fields --------
        numeric_fields = ["dni", "house_number"]

        for field in numeric_fields:
            value = payload.get(field)

            if value is None or value == "":
                payload[field] = None
                continue

            try:
                payload[field] = int(value)
            except Exception:
                messagebox.showerror("Error", f"{field} debe ser un número")
                return

        try:

            # -------- create person --------
            person_id = self.controller.create_person(payload)

            # -------- save memberships --------
            db_memberships = [
                {
                    "ministry_id": m.get("ministry_id"),
                    "area_id": m.get("area_id"),
                }
                for m in self._memberships
            ]

            if db_memberships:
                self.controller.update_memberships(
                    person_id,
                    db_memberships
                )

            messagebox.showinfo("OK", f"Persona creada con id={person_id}")

            # -------- clear form --------
            for e in self.entries.values():
                e.delete(0, "end")

            for combo in self.combos.values():
                combo.set("")

            if "baptized" in self.combos:
                self.combos["baptized"].set("No")

            self._memberships = []
            self._refresh_membership_listbox()

        except Exception as exc:
            messagebox.showerror("Error", str(exc))
