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
            # Ministry/Area (dropdown)
            ("ministry_id", "Ministerio"),
            ("area_id", "Área"),
                
            # Consolidation level (dropdown)
            ("consolidation_id", "Nivel de consolidación"),
            # CDB (dropdown)
            ("cdb", "¿CDB?"),
            ("baptized", "¿Bautizado?"),

        ]

        for i, (key, label) in enumerate(fields):
            lbl = tk.Label(self, text=label, bg=self.BG_PRIMARY, fg=self.TEXT_DARK)
            lbl.grid(row=i, column=0, sticky="w", padx=6, pady=3)
            
            if key == "ministry_area_id":
                # Dropdown for ministry areas
                combo = ttk.Combobox(self, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
                self._refresh_area_combo()
            elif key == "consolidation_id":
                # Dropdown for consolidation
                combo = ttk.Combobox(self, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
                self._refresh_consolidation_combo()
            elif key == "cdb":
                # Dropdown for CDB (house numbers)
                combo = ttk.Combobox(self, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
                self._refresh_cdb_combo()
            elif key == "ministry_id":
                combo = ttk.Combobox(self, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                combo.bind("<<ComboboxSelected>>", self._on_ministry_selected)
                self.combos[key] = combo
                self._refresh_ministry_combo()  
            elif key == "area_id":
                combo = ttk.Combobox(self, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
                self._refresh_area_combo()
            elif key == "baptized":
                combo = ttk.Combobox(self, width=37, state="readonly")
                combo["values"] = ["Sí", "No"]
                combo.current(1)  # default = No
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
            else:
                ent = tk.Entry(self, width=40, bg=self.BG_INPUT, fg=self.TEXT_DARK, relief="solid", bd=1)
                ent.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = ent

        btn = tk.Button(self, text="Agregar", command=self._on_submit, bg=self.BTN_COLOR, fg="white", relief="raised", bd=1, activebackground="#5A2A77")
        btn.grid(row=len(fields), column=0, columnspan=2, pady=(10, 0))
    
    def _refresh_area_combo(self):
        """Load ministry areas into the combo box."""
        if not self.config_service:
            return
        try:
            areas = self.config_service.get_all_areas()
            # Format: "Ministry - Area (ID)"
            self._area_options = []
            labels = []
            for area in areas:
                self._area_options.append(area["area_id"])
                ministry_name = area.get("ministry_name", "Unknown")
                label = f"{ministry_name} - {area['area']}"
                labels.append(label)
            self.combos["ministry_area_id"]["values"] = labels
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

    def _on_submit(self):
        payload = {k: (v.get() or None) for k, v in self.entries.items()}
        
        # Handle combo boxes
        # Get selected ministry
        min_idx = self.combos["ministry_id"].current()
        selected_ministry_id = None
        if min_idx >= 0 and hasattr(self, "_ministry_options"):
            selected_ministry_id = self._ministry_options[min_idx]["ministry_id"]

        # Get selected area
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
        
        # Consolidation
        cons_idx = self.combos["consolidation_id"].current()
        if cons_idx >= 0 and hasattr(self, "_consolidation_options"):
            payload["consolidation_id"] = self._consolidation_options[cons_idx]["consolidation_id"]
        else:
            payload["consolidation_id"] = None
        
        # CDB
        cdb_idx = self.combos["cdb"].current()
        if cdb_idx >= 0 and hasattr(self, "_cdb_options"):
            payload["cdb"] = self._cdb_options[cdb_idx]["cdb_id"]
        else:
            payload["cdb"] = None
        
        # Baptized (checkbox or default to False)
        baptized_val = self.combos["baptized"].get()
        payload["baptized"] = True if baptized_val == "Sí" else False

        
        # Convert numeric/boolean fields
        numeric_fields = ["dni", "house_number"]
        for field in numeric_fields:
            if payload.get(field):
                try:
                    payload[field] = int(payload[field])
                except Exception:
                    messagebox.showerror("Error", f"{field} debe ser un número")
                    return

        try:
            person_id = self.controller.add_person(payload)
            messagebox.showinfo("OK", f"Persona creada con id={person_id}")
            # Clear fields
            for e in self.entries.values():
                e.delete(0, "end")
            for combo in self.combos.values():
                combo.set("")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
    
    def refresh_dropdowns(self):
        """Refresh all dropdown lists (called when config changes)."""
        self._refresh_ministry_combo()
        self._refresh_area_combo()
        self._refresh_consolidation_combo()
        self._refresh_cdb_combo()