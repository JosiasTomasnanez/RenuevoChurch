from src.frontend.views._base import BaseFrame, tk, ttk

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

        # Define all available columns and their headers
        self._all_cols = (
            "person_id", "first_name", "last_name", "email", "birthdate",
            "dni", "phone_number", "marital_status", "social_security",
            "baptized", "cdb", "street", "neighborhood", "house_number",
            "ministry_area_id", "consolidation_id"
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
            "ministry_area_id": "Área Min.",
            "consolidation_id": "Consolidación",
        }

        # BooleanVars to track which columns are visible
        # Default: person_id, first_name, last_name, dni, phone_number, neighborhood
        _defaults = {"person_id", "first_name", "last_name", "dni", "phone_number", "neighborhood"}
        self._col_vars = {c: tk.BooleanVar(value=(c in _defaults)) for c in self._all_cols}

        # Columns selection menu - directly applies on click
        self.col_btn = tk.Menubutton(top, text="Columnas ▾", relief="raised")
        col_menu = tk.Menu(self.col_btn, tearoff=False)
        self.col_btn.config(menu=col_menu)
        for c in self._all_cols:
            col_menu.add_checkbutton(
                label=self._headers.get(c, c),
                variable=self._col_vars[c],
                command=self._on_columns_changed
            )
        self.col_btn.pack(side="left", padx=(6, 0))

        # Filters menu and active filter display
        self._active_filter_neighborhood = None
        self.filter_label = tk.Label(top, text="")
        self.filter_label.pack(side="left", padx=(6, 0))

        self.filter_btn = tk.Menubutton(top, text="Filtros ▾", relief="raised")
        filter_menu = tk.Menu(self.filter_btn, tearoff=False)
        self.filter_btn.config(menu=filter_menu)
        filter_menu.add_command(label="Barrio...", command=self._open_neighborhood_filter)
        filter_menu.add_separator()
        filter_menu.add_command(label="Limpiar filtro", command=self._clear_neighborhood_filter)
        self.filter_btn.pack(side="left", padx=(6, 0))

        # Create the results tree according to currently selected columns
        self._create_tree()

        # Allow double-click to open modify
        self.tree.bind("<Double-1>", self._on_modify_selected)
        self.tree.bind("<ButtonRelease-1>", self._maybe_action_click)

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
            self.tree.insert("", "end", values=tuple(values))

    def _get_cell_value(self, row, col):
        """Return the value for a given column key from a row which may be
        either a repository-style dict or a Person object.
        """
        if isinstance(row, dict):
            person = row.get("person") or {}
            if col in ("street", "neighborhood", "house_number"):
                addr = row.get("address") or {}
                return addr.get(col)
            else:
                return person.get(col)
        else:
            # Person object
            if col in ("street", "neighborhood", "house_number"):
                addr = getattr(row, "address", None)
                return getattr(addr, col, None) if addr is not None else None
            else:
                return getattr(row, col, None)

    def _visible_columns(self):
        return [c for c in self._all_cols if self._col_vars[c].get()]

    def _on_columns_changed(self):
        # recreate tree to reflect new column set and refresh contents
        self._create_tree()
        self._on_search()

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

    # clicking in table cells no longer triggers actions — we rely on
    # double-click to load the modify form. Keep a no-op method here in case
    # old code references it.
    def _maybe_action_click(self, event):
        return

    def _apply_filters(self, results):
        """Apply all active filters to a list of results.
        
        Filters are applied sequentially. This method is designed to be
        easily extended with new filters without modifying _on_search.
        """
        # Start with the full result set
        filtered = results[:]
        
        # Apply neighborhood filter if active
        if self._active_filter_neighborhood:
            filtered = self._filter_by_neighborhood(filtered, self._active_filter_neighborhood)
        
        # Add more filters here as needed:
        # filtered = self._filter_by_ministry(filtered, self._active_ministry)
        # filtered = self._filter_by_age_range(filtered, self._min_age, self._max_age)
        # etc.
        
        return filtered

    def _filter_by_neighborhood(self, results, neighborhood):
        """Filter results to only include those matching the given neighborhood."""
        filtered = []
        for r in results:
            neigh = self._get_cell_value(r, "neighborhood")
            if neigh == neighborhood:
                filtered.append(r)
        return filtered


    def _gather_neighborhoods(self):
        """Return a sorted list of unique neighborhoods available in the DB.

        Falls back to an empty list on error.
        """
        try:
            people = []
            try:
                people = self.controller.services.people.get_all_people()
            except Exception:
                # fall back to calling search with empty query
                try:
                    people = self.controller.search("")
                except Exception:
                    people = []

            neighs = set()
            for p in people:
                # support both dict and Person objects
                if isinstance(p, dict):
                    addr = p.get("address") or {}
                    n = addr.get("neighborhood")
                else:
                    addr = getattr(p, "address", None)
                    n = getattr(addr, "neighborhood", None) if addr is not None else None
                if n:
                    neighs.add(str(n))

            return sorted(neighs)
        except Exception:
            return []

    def _open_neighborhood_filter(self):
        """Open a small popup listing neighborhoods to choose from."""
        neighs = self._gather_neighborhoods()
        win = tk.Toplevel(self)
        win.title("Seleccionar barrio")
        win.geometry("300x300")

        lb = tk.Listbox(win)
        for n in neighs:
            lb.insert("end", n)
        lb.pack(fill="both", expand=True, padx=6, pady=6)

        # pre-select current neighborhood if set
        if self._active_filter_neighborhood:
            try:
                idx = neighs.index(self._active_filter_neighborhood)
                lb.selection_set(idx)
                lb.see(idx)
            except Exception:
                pass

        frm = tk.Frame(win)
        frm.pack(fill="x", padx=6, pady=6)
        def _on_ok():
            sel = lb.curselection()
            if not sel:
                win.destroy()
                return
            val = lb.get(sel[0])
            self._apply_neighborhood_filter(val)
            win.destroy()

        def _on_cancel():
            win.destroy()

        tk.Button(frm, text="Aplicar", command=_on_ok).pack(side="left", padx=(0,6))
        tk.Button(frm, text="Cancelar", command=_on_cancel).pack(side="left")

    def _apply_neighborhood_filter(self, neighborhood: str):
        self._active_filter_neighborhood = neighborhood
        if neighborhood:
            self.filter_label.config(text=f"Filtro barrio: {neighborhood}")
        else:
            self.filter_label.config(text="")
        # Re-run search to apply the filter
        self._on_search()

    def _clear_neighborhood_filter(self):
        self._active_filter_neighborhood = None
        self.filter_label.config(text="")
        # Re-run search to clear the filter
        self._on_search()
