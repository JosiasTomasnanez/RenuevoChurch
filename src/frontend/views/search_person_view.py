from src.frontend.views._base import BaseFrame, tk, ttk


class SearchPersonFrame(BaseFrame):
    # Pastel color scheme
    BG_PRIMARY = "#F0E6F6"      # Light purple
    BG_INPUT = "#FFFBF5"        # Warm white
    BTN_COLOR = "#7A4A97"       # Strong dark purple
    TEXT_DARK = "#5A5A5A"       # Dark gray for text
    
    def __init__(self, master, controller, config_service=None, open_modify_callback=None, **kwargs):
        if tk is None:
            raise RuntimeError("Tkinter not available in this environment — run GUI on a machine with Tk installed")
        # accept optional config_service and remove custom kwargs
        super().__init__(master, **{k: v for k, v in kwargs.items() if k not in ('open_modify_callback', 'config_service')})
        self.controller = controller
        self.config_service = config_service
        self._open_modify_cb = open_modify_callback
        self.config(bg=self.BG_PRIMARY)
        
        # Initialize columns and filters before _build()
        # Nota: la información de ministerios/áreas se muestra en el panel
        # de detalles inferior, por eso no hay una columna visible de "Ministerio".
        self._all_cols = (
            "person_id", "first_name", "last_name", "email", "birthdate",
            "dni", "phone_number", "marital_status", "social_security",
            "baptized", "cdb", "street", "neighborhood", "house_number",
            "consolidation_id",
            "ministry"
        )
        self._headers = {
            "person_id": "ID",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo",
            "birthdate": "Fecha Nac.",
            "dni": "DNI",
            "phone_number": "Teléfono",
            "marital_status": "Estado Civil",
            "social_security": "Seguro Social",
            "baptized": "Bautizado",
            "cdb": "CDB",
            "street": "Calle",
            "neighborhood": "Barrio",
            "house_number": "Nro Casa",
            "consolidation_id": "Consolidación",
            "ministry": "Ministerio"
        }
        _defaults = {"person_id", "first_name", "last_name", "dni", "phone_number", "neighborhood"}
        self._col_vars = {c: tk.BooleanVar(value=(c in _defaults)) for c in self._all_cols}
        self._active_filters = {
            "neighborhood": None,
            "ministry": None,
            "cdb": None,
        }
        
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=self.BG_PRIMARY)
        top.pack(fill="x", padx=6, pady=6)
        
        # Left side: search and modify button
        left_frame = tk.Frame(top, bg=self.BG_PRIMARY)
        left_frame.pack(side="left", fill="x")
        
        tk.Label(left_frame, text="Buscar por nombre o apellido:", bg=self.BG_PRIMARY, fg=self.TEXT_DARK).pack(side="left")
        self.search_entry = tk.Entry(left_frame, bg=self.BG_INPUT, fg=self.TEXT_DARK, relief="solid", bd=1, width=25)
        self.search_entry.pack(side="left", padx=6)
        search_btn = tk.Button(left_frame, text="Buscar", command=self._on_search, bg=self.BTN_COLOR, fg="white", relief="raised", bd=1, activebackground="#5A2A77")
        search_btn.pack(side="left")
        
        # Button to modify selected person (disabled until selection)
        self.modify_btn = tk.Button(left_frame, text="Modificar", command=self._on_modify_button, state="disabled", bg=self.BTN_COLOR, fg="white", relief="raised", bd=1, activebackground="#5A2A77", disabledforeground="#999999")
        self.modify_btn.pack(side="left", padx=3)
        
        # Right side: columns and filters buttons
        right_frame = tk.Frame(top, bg=self.BG_PRIMARY)
        right_frame.pack(side="right", fill="x")
        
        # Columns selection menu
        self.col_btn = tk.Menubutton(right_frame, text="Columnas ▾", relief="raised", bg=self.BTN_COLOR, fg="white", activebackground="#5A2A77", activeforeground="white")
        col_menu = tk.Menu(self.col_btn, tearoff=False)
        self.col_btn.config(menu=col_menu)
        for c in self._all_cols:
            col_menu.add_checkbutton(
                label=self._headers.get(c, c),
                variable=self._col_vars[c],
                command=self._on_columns_changed
            )
        self.col_btn.pack(side="left", padx=(0, 3))
        
        # Filter label
        self.filter_label = tk.Label(right_frame, text="", bg=self.BG_PRIMARY, fg=self.TEXT_DARK)
        self.filter_label.pack(side="left", padx=(6, 0))
        
        # Filters menu
        self.filter_btn = tk.Menubutton(right_frame, text="Filtros ▾", relief="raised", bg=self.BTN_COLOR, fg="white", activebackground="#5A2A77", activeforeground="white")
        filter_menu = tk.Menu(self.filter_btn, tearoff=False)
        self.filter_btn.config(menu=filter_menu)
        filter_menu.add_command(label="Barrio...", command=lambda: self._open_filter("neighborhood", "Seleccionar barrio"))
        filter_menu.add_command(label="Ministerio...", command=lambda: self._open_filter("ministry", "Seleccionar ministerio"))
        filter_menu.add_command(label="CDB...", command=lambda: self._open_filter("cdb", "Seleccionar CDB"))
        filter_menu.add_separator()
        filter_menu.add_command(label="Limpiar filtros", command=self._clear_all_filters)
        self.filter_btn.pack(side="left", padx=3)

        # Create the results tree according to currently selected columns
        self._create_tree()

        # Details panel for memberships (ministries/areas)
        self._build_details_panel()
        self.details_frame.pack_forget()
        # Allow double-click to open modify (bonus) and track selection for button
        self.tree.bind("<Double-1>", self._on_modify_selected)
        self.tree.bind("<ButtonRelease-1>", self._on_tree_select)
        self.tree.bind("<KeyRelease>", self._on_tree_select)

        # Load all people initially
        self._on_search()

    def _on_search(self):
        q = self.search_entry.get().strip()
        # First, search normally (by name)
        results = self.controller.search(q)
        
        # Then apply active filters to the search results
        filtered_results = self._apply_filters(results)
        
        # Populate tree with filtered results
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in filtered_results:
            values = []
            for col in self._visible_columns():
                values.append(self._get_cell_value(r, col))
            # ensure we can always identify the person even if ID column hidden
            pid = self._get_person_id(r)
            iid = str(pid) if pid is not None else None
            if iid:
                self.tree.insert("", "end", iid=iid, values=tuple(values))
            else:
                self.tree.insert("", "end", values=tuple(values))

        # Update details panel based on current selection (if any)
        self._update_details_panel()

    def _get_cell_value(self, row, col):
        # row es un objeto Person
        # Mostrar número de CDB en lugar de su id
        if col == "ministry":
            name = self._get_person_ministry_name(row)
            return "" if name is None else name
        
        if col == "cdb":
            try:
                cdb_id = getattr(row, "cdb", None)
            except Exception:
                cdb_id = None
            if cdb_id is None:
                return ""
            try:
                # Prefer injected config_service (frontend controller), fallback to controller.services
                if hasattr(self, "config_service") and self.config_service is not None:
                    cdb = self.config_service.get_cdb_by_id(cdb_id)
                else:
                    # try to use backend services if available
                    svc = getattr(self.controller, "services", None)
                    if svc is not None:
                        cfg = getattr(svc, "config", None)
                        if cfg is not None:
                            cdb = cfg.get_cdb_by_id(cdb_id)
                        else:
                            cdb = None
                    else:
                        cdb = None

                if isinstance(cdb, dict):
                    return "" if cdb.get("number") is None else str(cdb.get("number"))
                return str(cdb_id)
            except Exception:
                return str(cdb_id)
        # columnas de la persona
        if hasattr(row, col):
            val = getattr(row, col)
            return "" if val is None else val

        # columnas de dirección
        if hasattr(row, "address") and row.address:
            if hasattr(row.address, col):
                val = getattr(row.address, col)
                return "" if val is None else val

        return ""




    def _visible_columns(self):
        return [c for c in self._all_cols if self._col_vars[c].get()]

    def _on_columns_changed(self):
        self._create_tree()
        self._on_search()

        if self._col_vars.get("ministry") and self._col_vars["ministry"].get():
            self.details_frame.pack(fill="x", padx=6, pady=(0, 6))
        else:
            self.details_frame.pack_forget()

    def _create_tree(self):
        # destroy existing tree if present
        try:
            self.tree.destroy()
        except Exception:
            pass

        cols = self._visible_columns()
        # fallback: if no columns selected show at least ID
        if not cols:
            cols = ["person_id"]
            self._col_vars["person_id"].set(True)

        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=self._headers.get(c, c))
            self.tree.column(c, width=120, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

    def _build_details_panel(self):
        """Build a panel to show ministries/areas for the selected person."""

        self.details_frame = tk.Frame(self, bg=self.BG_PRIMARY)
        self.details_frame.pack(fill="x", padx=6, pady=(0, 6))

        top_row = tk.Frame(self.details_frame, bg=self.BG_PRIMARY)
        top_row.pack(fill="x")

        tk.Label(
            top_row,
            text="Ministerios / Áreas:",
            bg=self.BG_PRIMARY,
            fg=self.TEXT_DARK,
        ).pack(side="left")

        # botón cargar
        tk.Button(
            top_row,
            text="Cargar",
            command=self._load_memberships,
            bg=self.BTN_COLOR,
            fg="white",
            relief="raised",
            bd=1,
            activebackground="#5A2A77"
        ).pack(side="right")

        self.details_list = tk.Listbox(
            self.details_frame,
            height=4,
            bg=self.BG_INPUT,
            fg=self.TEXT_DARK,
            relief="solid",
            bd=1,
        )

        self.details_list.pack(fill="x", padx=0, pady=(4, 0))

   
    def _load_memberships(self):
        """Load ministries for the selected person when pressing button."""

        self.details_list.delete(0, "end")

        sel = self.tree.selection()
        if not sel:
            return

        item = sel[0]

        try:
            pid = int(item)
        except Exception:
            values = self.tree.item(item, "values")
            if not values:
                return
            try:
                pid = int(values[0])
            except Exception:
                return

        memberships = []

        try:
            # usar mismo método que Modify
            if hasattr(self.controller, "get_memberships"):
                memberships = self.controller.get_memberships(pid) or []
        except Exception:
            memberships = []

        if not memberships:
            self.details_list.insert("end", "Sin ministerios")
            return

        for rm in memberships:

            ministry = rm.get("ministry") or {}
            area = rm.get("area") or {}

            ministry_name = ministry.get("name") or ""
            area_name = area.get("area") or ""

            if ministry_name and area_name:
                label = f"{ministry_name} / {area_name}"
            elif ministry_name:
                label = ministry_name
            elif area_name:
                label = area_name
            else:
                label = "(sin nombre)"

            self.details_list.insert("end", label)
   
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
        # Prefer using the item's iid which we set to person_id when inserting
        try:
            pid = int(item)
        except Exception:
            # Fallback: try to read first value (legacy)
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

    def _on_tree_select(self, event=None):
        """Track tree selection and enable/disable modify button."""
        sel = self.tree.selection()
        if sel:
            self.modify_btn.config(state="normal")
        else:
            self.modify_btn.config(state="disabled")


    def _on_modify_button(self):
        """Load the selected person into modify frame when button clicked."""
        sel = self.tree.selection()
        if not sel:
            return
        
        item = sel[0]
        try:
            # Try to use iid as person_id (set when inserting rows)
            pid = int(item)
        except Exception:
            # Fallback: try to read first value
            values = self.tree.item(item, "values")
            if not values:
                return
            try:
                pid = int(values[0])
            except Exception:
                return

        if self._open_modify_cb:
            self._open_modify_cb(pid, show=True)

    def _apply_filters(self, results):
        """Apply all active filters in `self._active_filters` sequentially."""
        filtered = results[:]
        for fname, val in self._active_filters.items():
            if val is not None:
                filtered = self._filter_by(filtered, fname, val)
        return filtered

    def _filter_by(self, results, filter_name, value):
        """Generic filter dispatcher."""
        if filter_name == "neighborhood":
            return [r for r in results if self._get_cell_value(r, "neighborhood") == value]
        if filter_name == "ministry":
            # Filter by ministry using memberships (backend service) when possible.
            try:
                svc = getattr(self.controller, "services", None)
                cfg = self.config_service

                # Resolve ministry_id from its name using config_service if available
                ministry_id = None
                if cfg is not None:
                    ministries = cfg.get_all_ministries()
                    for m in ministries:
                        if m.get("name") == value:
                            ministry_id = m.get("ministry_id")
                            break
                if ministry_id is not None and svc is not None:
                    people_svc = getattr(svc, "people", None)
                    if people_svc is not None:
                        matched_people = self.controller.get_people_by_ministry(ministry_id)
                        allowed_ids = {self._get_person_id(p) for p in matched_people}
                        return [
                            r
                            for r in results
                            if self._get_person_id(r) in allowed_ids
                        ]
            except Exception:
                # Fallback to previous behaviour using single ministry name
                return [r for r in results if self._get_person_ministry_name(r) == value]
            # If we couldn't resolve ministry via backend, fall back to name-based filter
            return [r for r in results if self._get_person_ministry_name(r) == value]
        if filter_name == "cdb":
            # compare by CDB number (string)
            return [r for r in results if self._get_person_cdb_number(r) == str(value)]
        return results

    def _gather_options(self, filter_name):
        """Return available options for a filter (neighborhood or ministry)."""
        try:
            people = []
            try:
                people = self.controller.services.people.get_all_people()
            except Exception:
                try:
                    people = self.controller.search("")
                except Exception:
                    people = []

            if filter_name == "neighborhood":
                vals = set()
                for p in people:
                    if isinstance(p, dict):
                        addr = p.get("address") or {}
                        n = addr.get("neighborhood")
                    else:
                        addr = getattr(p, "address", None)
                        n = getattr(addr, "neighborhood", None) if addr is not None else None
                    if n:
                        vals.add(str(n))
                return sorted(vals)

            if filter_name == "ministry":
                # Prefer listing all configured ministries so the filter sees
                # ministries even if nobody is currently assigned in primary slot.
                try:
                    if (
                        hasattr(self, "config_service")
                        and self.config_service is not None
                    ):
                        mins = self.config_service.get_all_ministries()
                        names = [m.get("name") for m in mins if m.get("name")]
                        if names:
                            return sorted(set(names))
                except Exception:
                    pass

                # Fallback: infer from current people (using primary ministry only)
                vals = set()
                for p in people:
                    name = self._get_person_ministry_name(p)
                    if name:
                        vals.add(name)
                return sorted(vals)

            if filter_name == "cdb":
                # Prefer using config_service to list all CDB numbers
                try:
                    if hasattr(self, "config_service") and self.config_service is not None:
                        cdbs = self.config_service.get_all_cdb_options()
                        return sorted([str(c.get("number")) for c in cdbs if c.get("number") is not None])
                except Exception:
                    pass

                # Fallback: collect from people and resolve ids
                vals = set()
                for p in people:
                    num = self._get_person_cdb_number(p)
                    if num:
                        vals.add(str(num))
                return sorted(vals)

            return []
        except Exception:
            return []

    def _get_person_ministry_name(self, p):
        """Return the ministry name for a person result (supports dict or Person object).

        Returns the ministry name string or None.
        """
        # dict-shaped row (repository returns nested dicts)
        try:
            if isinstance(p, dict):
                # nested mode: p.get('ministry') or p.get('person') flattened
                m = p.get("ministry") if isinstance(p, dict) else None
                if m and isinstance(m, dict):
                    name = m.get("name")
                    if name:
                        return str(name)
                # flattened person
                person = p.get("person") or p
                name = person.get("ministry") if isinstance(person, dict) else None
                if name:
                    return str(name)
                return None

            # object mode (Person instance)
            ministry = getattr(p, "ministry", None)
            if ministry:
                try:
                    return getattr(ministry, "name")
                except Exception:
                    return None
        except Exception:
            return None
        return None

    def _get_person_id(self, p):
        """Extract the person_id from a person result (dict or Person object)."""
        try:
            if isinstance(p, dict):
                # nested dict shape: {"person": {...}, ...} or flattened person dict
                person = p.get("person") if "person" in p else p
                if isinstance(person, dict):
                    val = person.get("person_id")
                    if val is not None:
                        try:
                            return int(val)
                        except Exception:
                            return None
                return None

            # object mode (Person instance)
            pid = getattr(p, "person_id", None)
            if pid is None:
                return None
            try:
                return int(pid)
            except Exception:
                return None
        except Exception:
            return None

    def _get_person_cdb_number(self, p):
        """Return the CDB number (as string) for a person result (dict or Person object)."""
        try:
            # extract cdb id
            cdb_id = None
            if isinstance(p, dict):
                person = p.get("person") if isinstance(p, dict) and "person" in p else p
                if isinstance(person, dict):
                    cdb_id = person.get("cdb")
                else:
                    cdb_id = None
            else:
                cdb_id = getattr(p, "cdb", None)

            if cdb_id is None:
                return None

            # resolve id -> number using config_service when available
            try:
                if hasattr(self, "config_service") and self.config_service is not None:
                    cdb = self.config_service.get_cdb_by_id(cdb_id)
                    if isinstance(cdb, dict) and cdb.get("number") is not None:
                        return str(cdb.get("number"))
                # fallback to backend services if available
                svc = getattr(self.controller, "services", None)
                if svc is not None:
                    cfg = getattr(svc, "config", None)
                    if cfg is not None:
                        try:
                            cdb = cfg.get_cdb_by_id(cdb_id)
                            if isinstance(cdb, dict) and cdb.get("number") is not None:
                                return str(cdb.get("number"))
                        except Exception:
                            pass
            except Exception:
                pass

            # final fallback: return the id as string
            return str(cdb_id)
        except Exception:
            return None

    def _open_filter(self, filter_name, title):
        """Open a reusable popup to select a filter value."""
        options = self._gather_options(filter_name)
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("300x300")
        win.config(bg=self.BG_PRIMARY)

        lb = tk.Listbox(win, bg=self.BG_INPUT, fg=self.TEXT_DARK, relief="solid", bd=1)
        for o in options:
            lb.insert("end", o)
        lb.pack(fill="both", expand=True, padx=6, pady=6)

        # pre-select current value if present
        cur = self._active_filters.get(filter_name)
        if cur:
            try:
                idx = options.index(cur)
                lb.selection_set(idx)
                lb.see(idx)
            except Exception:
                pass

        frm = tk.Frame(win, bg=self.BG_PRIMARY)
        frm.pack(fill="x", padx=6, pady=6)

        def _on_ok():
            sel = lb.curselection()
            if not sel:
                win.destroy()
                return
            val = lb.get(sel[0])
            self._apply_filter(filter_name, val)
            win.destroy()

        def _on_cancel():
            win.destroy()

        tk.Button(frm, text="Aplicar", command=_on_ok, bg=self.BTN_COLOR, fg="white", relief="raised", bd=1, activebackground="#5A2A77").pack(side="left", padx=(0,6))
        tk.Button(frm, text="Cancelar", command=_on_cancel, bg="#A83030", fg="white", relief="raised", bd=1, activebackground="#8A1010").pack(side="left")

    def _apply_filter(self, filter_name, value):
        self._active_filters[filter_name] = value
        # build compact status label from active filters
        parts = []
        if self._active_filters.get("neighborhood"):
            parts.append(f"barrio: {self._active_filters.get('neighborhood')}")
        if self._active_filters.get("ministry"):
            parts.append(f"ministerio: {self._active_filters.get('ministry')}")
        self.filter_label.config(text=("Filtro " + " | ".join(parts)) if parts else "")
        self._on_search()

    def _update_details_panel(self):
        """Populate the details panel with ministries/areas for the selected person."""
        if not hasattr(self, "details_list"):
            return

        self.details_list.delete(0, "end")

        sel = self.tree.selection() if hasattr(self, "tree") else ()
        if not sel:
            return

        item = sel[0]
        pid = None
        try:
            pid = int(item)
        except Exception:
            values = self.tree.item(item, "values")
            if values:
                try:
                    pid = int(values[0])
                except Exception:
                    pid = None

        if pid is None:
            return

        # Fetch memberships via controller (delegates to backend service)
        memberships = []
        try:
            svc = getattr(self.controller, "services", None)
            if svc is not None:
                people_svc = getattr(svc, "people", None)
                if people_svc is not None:
                    memberships = self.controller.get_memberships(pid) or []
        except Exception:
            memberships = []

        if not memberships:
            # If there are no memberships stored yet, at least show primary ministry/area if present
            # by reusing the existing helpers.
            # We need the Person object corresponding to this row; easiest is to search in latest results.
            return

        for m in memberships:
            ministry = m.get("ministry") or {}
            area = m.get("area") or {}
            min_name = ministry.get("name") or ""
            area_name = area.get("area") or ""

            if min_name and area_name:
                label = f"{min_name} / {area_name}"
            elif min_name:
                label = min_name
            elif area_name:
                label = area_name
            else:
                label = "(sin nombre)"

            self.details_list.insert("end", label)

    def refresh_dropdowns(self):
        """Refresh search results to reflect updated config."""
        # Simply re-run the current search to update all displayed data
        self._on_search()

    def _clear_all_filters(self):
        for k in list(self._active_filters.keys()):
            self._active_filters[k] = None
        self.filter_label.config(text="")
        self._on_search()

