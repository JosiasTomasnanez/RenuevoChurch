from src.frontend.views._base import BaseFrame, tk, ttk
from src.frontend.helpers.config_dropdown_helper import ConfigDropdownHelper
from datetime import datetime

class SearchPersonFrame(BaseFrame):
    BG_PRIMARY = "#F0E6F6"
    BG_INPUT = "#FFFBF5"
    BTN_COLOR = "#7A4A97"
    TEXT_DARK = "#5A5A5A"
    
    def __init__(self, master, controller, config_service=None, open_modify_callback=None, **kwargs):
        super().__init__(master, **{k: v for k, v in kwargs.items() if k not in ('open_modify_callback', 'config_service')})
        self.controller = controller
        self.config_service = config_service
        self._open_modify_cb = open_modify_callback
        self.config(bg=self.BG_PRIMARY)
        
        self.drop_helper = ConfigDropdownHelper(self.config_service)
        
        # Columnas disponibles
        self._all_cols = (
            "person_id", "first_name", "last_name","gender", "dni","birthdate","age", "neighborhood", 
            "phone_number", "baptized", "cdb", "consolidation_id"
        )
        self._headers = {
            "person_id": "ID", "first_name": "Nombre", "last_name": "Apellido",
            "gender": "Género", "dni": "DNI", "birthdate": "Fec. Nac.", "age": "Edad", "neighborhood": "Barrio", "phone_number": "Teléfono",
            "baptized": "Bautizado", "cdb": "CDB", "consolidation_id": "Consolidación"
        }
        
        _defaults = {"person_id", "first_name", "last_name", "dni", "neighborhood"}
        self._col_vars = {c: tk.BooleanVar(value=(c in _defaults)) for c in self._all_cols}
        
        self._active_filters = {"neighborhood": None, "ministry": None, "cdb": None}
        
        self._build()

    def _build(self):
        # --- TOP BAR ---
        top = tk.Frame(self, bg=self.BG_PRIMARY)
        top.pack(fill="x", padx=6, pady=6)
        
        search_lbl = tk.Label(top, text="Buscar:", bg=self.BG_PRIMARY, fg=self.TEXT_DARK)
        search_lbl.pack(side="left")
        
        self.search_entry = tk.Entry(top, bg=self.BG_INPUT, width=25)
        self.search_entry.pack(side="left", padx=6)
        self.search_entry.bind("<Return>", lambda e: self._on_search())
        
        tk.Button(top, text="Buscar", command=self._on_search, bg=self.BTN_COLOR, fg="white").pack(side="left", padx=2)
        
        self.modify_btn = tk.Button(top, text="Modificar", command=self._on_modify_button, 
                                   state="disabled", bg=self.BTN_COLOR, fg="white")
        self.modify_btn.pack(side="left", padx=10)

        # Filtro Label Dinámico
        self.filter_info_lbl = tk.Label(top, text="", bg=self.BG_PRIMARY, fg="#A040A0", font=("Arial", 9, "bold"))
        self.filter_info_lbl.pack(side="left", padx=10)

        # --- BOTONES DERECHA ---
        r_frame = tk.Frame(top, bg=self.BG_PRIMARY)
        r_frame.pack(side="right")
        
        col_mb = tk.Menubutton(r_frame, text="Columnas ▾", relief="raised", bg=self.BTN_COLOR, fg="white")
        col_menu = tk.Menu(col_mb, tearoff=False)
        for c in self._all_cols:
            col_menu.add_checkbutton(label=self._headers[c], variable=self._col_vars[c], command=self._create_tree)
        col_mb.config(menu=col_menu)
        col_mb.pack(side="left", padx=2)

        filt_mb = tk.Menubutton(r_frame, text="Filtros ▾", relief="raised", bg=self.BTN_COLOR, fg="white")
        filt_menu = tk.Menu(filt_mb, tearoff=False)
        filt_menu.add_command(label="Barrio...", command=lambda: self._open_filter("neighborhood"))
        filt_menu.add_command(label="Ministerio...", command=lambda: self._open_filter("ministry"))
        filt_menu.add_command(label="CDB...", command=lambda: self._open_filter("cdb"))
        filt_menu.add_separator()
        filt_menu.add_command(label="Limpiar Filtros", command=self._clear_all_filters)
        filt_mb.config(menu=filt_menu)
        filt_mb.pack(side="left", padx=2)

        # --- TREEVIEW ---
        self.tree_container = tk.Frame(self, bg=self.BG_PRIMARY)
        self.tree_container.pack(fill="both", expand=True, padx=6)
        self._create_tree()

        # --- DETAILS ---
        self.details_frame = tk.LabelFrame(self, text=" Ministerios en los que participa ", bg=self.BG_PRIMARY, fg=self.TEXT_DARK)
        self.details_frame.pack(fill="x", padx=6, pady=10)
        self.details_list = tk.Listbox(self.details_frame, height=3, bg=self.BG_INPUT, relief="flat")
        self.details_list.pack(fill="x", padx=5, pady=5)

    def _create_tree(self):
        if hasattr(self, 'tree'): self.tree.destroy()
        cols = [c for c in self._all_cols if self._col_vars[c].get()]
        self.tree = ttk.Treeview(self.tree_container, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=self._headers[c])
            self.tree.column(c, width=100)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self._on_modify_button())
        self._on_search()

    def _on_search(self):
        query = self.search_entry.get().strip()
        results = self.controller.search_people(query)
        filtered = self._apply_filters(results)

        self.tree.delete(*self.tree.get_children())
        visible_cols = [c for c in self._all_cols if self._col_vars[c].get()]

        for p in filtered:
            values = [self._get_formatted_value(p, col) for col in visible_cols]
            self.tree.insert("", "end", iid=str(p["person_id"]), values=values)

    def _get_formatted_value(self, p, col):
        """Extrae y formatea valores de la persona 'p' para la columna 'col'."""

        if col == "age":
            bday = p.get("birthdate")
            if not bday: return ""
            try:
                bday_dt = datetime.strptime(bday, "%Y-%m-%d").date() if isinstance(bday, str) else bday
                today = datetime.now().date()
                age = today.year - bday_dt.year - ((today.month, today.day) < (bday_dt.month, bday_dt.day))
                return f"{age} años"
            except:
                return ""
        val = p.get(col)
        if val is None and isinstance(p.get("address"), dict):
            val = p.get("address").get(col)
        if col == "gender":
            return val if val else ""
        if col == "baptized":
            return "Sí" if val else "No"
        if col == "birthdate" and val:
            try:
                d = datetime.strptime(str(val), "%Y-%m-%d")
                return d.strftime("%d/%m/%Y")
            except:
                return val
        if col == "consolidation_id" and val:
            obj = self.drop_helper.find_consolidation_by_id(val)
            return obj["level"] if obj else f"ID: {val}"
        if col == "cdb" and val:
            obj = self.drop_helper.find_cdb_by_id(val)
            return f"CDB {obj['number']}" if obj else f"ID: {val}"
        return str(val) if val is not None else ""

    def _on_tree_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            self.modify_btn.config(state="disabled")
            return
        
        self.modify_btn.config(state="normal")
        self.details_list.delete(0, tk.END)
        try:
            pid = int(sel[0])
            mems = self.controller.get_memberships(pid) or []
            if not mems: self.details_list.insert(tk.END, "Sin asignaciones")
            for m in mems:
                txt = f"• {m['ministry']['name']}"
                if m.get('area'): txt += f" / {m['area']['area']}"
                self.details_list.insert(tk.END, txt)
        except: pass


    def refresh_dropdowns(self):
        self.drop_helper.refresh_all()
        self._on_search()

 
 
 
    def _get_formatted_value(self, p, col):
        """Extrae y formatea valores, incluyendo el cálculo de edad al vuelo."""
    
        if col == "age":
            bday = p.get("birthdate")
            if not bday: 
                return ""
            try:
                if isinstance(bday, str):
                    bday_dt = datetime.strptime(bday, "%Y-%m-%d").date()
                else:
                    bday_dt = bday
                
                today = datetime.now().date()
                age = today.year - bday_dt.year - ((today.month, today.day) < (bday_dt.month, bday_dt.day))
                return f"{age} años"
            except:
                return ""

  
        val = p.get(col)
    
        if val is None:
            addr = p.get("address")
            if isinstance(addr, dict): 
                val = addr.get(col)
    
        if col == "consolidation_id" and val:
            obj = self.drop_helper.find_consolidation_by_id(val)
            return obj["level"] if obj else f"ID: {val}"
    
        if col == "cdb" and val:
            obj = self.drop_helper.find_cdb_by_id(val)
            return f"CDB {obj['number']}" if obj else f"ID: {val}"
        
        if col == "baptized":
            return "Sí" if val else "No"
        
        if col == "birthdate" and val:
            try:
                d = datetime.strptime(str(val), "%Y-%m-%d")
                return d.strftime("%d/%m/%Y")
            except:
                return val
            
        return val if val is not None else ""
 
 

    def _apply_filters(self, results):
        """Aplica los filtros activos de forma segura."""
        f = self._active_filters
        res = results
        
        if f["neighborhood"]:
            # Filtro seguro para barrios (considerando que address puede ser None)
            res = [p for p in res if isinstance(p.get("address"), dict) and p["address"].get("neighborhood") == f["neighborhood"]]
        
        if f["cdb"]:
            res = [p for p in res if str(p.get("cdb")) == str(f["cdb"])]
            
        if f["ministry"]:
            try:
                m_id = self.drop_helper.get_ministry_id(f["ministry"])
                if m_id:
                    people_in_min = self.controller.get_people_by_ministry(m_id)
                    allowed_ids = {p["person_id"] for p in people_in_min}
                    res = [p for p in res if p["person_id"] in allowed_ids]
            except:
                pass
            
        return res

    def _on_modify_button(self):
        """Captura el ID seleccionado y dispara el salto a la otra pestaña."""
        sel = self.tree.selection()
        if not sel:
            return
        
        try:
            pid = int(sel[0]) # El iid que pusimos en el insert
            if self._open_modify_cb:
                # Llamamos al callback. En el main esto ejecutará _open_modify(pid)
                self._open_modify_cb(pid) 
        except Exception as e:
            print(f"Error al intentar modificar: {e}")

    def _open_filter(self, name):
        """Popup de filtro blindado contra NoneTypes."""
        win = tk.Toplevel(self)
        win.title(f"Filtrar por {name}")
        win.geometry("300x400")
        win.config(bg=self.BG_PRIMARY)
        
        lb = tk.Listbox(win, bg=self.BG_INPUT, fg=self.TEXT_DARK)
        lb.pack(fill="both", expand=True, padx=10, pady=10)
        
        options = []
        if name == "neighborhood":
            all_p = self.controller.search_people("")
            neighborhoods = set()
            for p in all_p:
                # CHEQUEO SEGURO DE DIRECCIÓN
                addr = p.get("address")
                if isinstance(addr, dict):
                    barrio = addr.get("neighborhood")
                    if barrio:
                        neighborhoods.add(barrio)
            options = sorted(list(neighborhoods))
        
        elif name == "ministry":
            self.drop_helper.refresh_all()
            options = [m["name"] for m in self.drop_helper._ministry_cache]
            
        elif name == "cdb":
            self.drop_helper.refresh_all()
            options = [f"CDB {c['number']}" for c in self.drop_helper._cdb_cache]

        for o in options: 
            lb.insert(tk.END, o)

        def apply():
            selection = lb.curselection()
            if selection:
                val = lb.get(selection[0])
                if name == "cdb":
                    num = val.replace("CDB ", "")
                    cdb_obj = next((c for c in self.drop_helper._cdb_cache if str(c['number']) == num), None)
                    self._active_filters[name] = cdb_obj["cdb_id"] if cdb_obj else None
                else:
                    self._active_filters[name] = val
                
                self.filter_info_lbl.config(text=f"Filtro: {val}")
                self._on_search()
                win.destroy()

        tk.Button(win, text="Aplicar Filtro", command=apply, bg=self.BTN_COLOR, fg="white").pack(pady=10)
    
    def _clear_all_filters(self):
        self._active_filters = {k: None for k in self._active_filters}
        self.filter_info_lbl.config(text="")
        self._on_search()