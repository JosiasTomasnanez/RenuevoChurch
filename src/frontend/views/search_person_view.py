from src.frontend.views._base import BaseFrame, tk, ttk
from src.frontend.helpers.config_dropdown_helper import ConfigDropdownHelper
from datetime import datetime
from tkinter import messagebox

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
        
        # Control de la vista inferior: "ministry" u "occupation"
        self.current_view = "ministry"
        
        # Columnas disponibles
        self._all_cols = (
            "person_id", "first_name", "last_name","gender","marital_status","membership_status",  "dni","social_security","birthdate","age", "neighborhood", 
            "phone_number","trusted_person_info", "baptized", "cdb", "consolidation_id"
        )
        self._headers = {
            "person_id": "ID", "first_name": "Nombre", "last_name": "Apellido",
            "gender": "Género","marital_status": "Estado Civil", "membership_status": "Estado de Membresía", "dni": "DNI",
            "social_security": "Obra Social", "birthdate": "Fec. Nac.", "age": "Edad",
            "neighborhood": "Barrio", "phone_number": "Teléfono","trusted_person_info": "Contacto de Emergencia",
            "baptized": "Bautizado", "cdb": "CDB", "consolidation_id": "Consolidación"
        }
        
        _defaults = {"person_id", "first_name", "last_name", "dni", "neighborhood"}
        self._col_vars = {c: tk.BooleanVar(value=(c in _defaults)) for c in self._all_cols}
        
        self._active_filters = {"neighborhood": None, "ministry": None,
                                "cdb": None, "marital_status": None,
                                "membership_status": None, "occupation": None,
                                "age_range": None,
                                "gender": None, "consolidation_id": None
                                }

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

        self.results_count_lbl = tk.Label(
            r_frame, 
            text="Resultados: 0", 
            bg=self.BG_PRIMARY, 
            fg=self.TEXT_DARK, 
            font=("Arial", 9, "bold")
        )
        self.results_count_lbl.pack(side="left", padx=(0, 15))

        col_mb = tk.Menubutton(r_frame, text="Columnas ▾", relief="raised", bg=self.BTN_COLOR, fg="white")
        col_menu = tk.Menu(col_mb, tearoff=False)
        for c in self._all_cols:
            col_menu.add_checkbutton(label=self._headers[c], variable=self._col_vars[c], command=self._create_tree)
        col_mb.config(menu=col_menu)
        col_mb.pack(side="left", padx=2)

        filt_mb = tk.Menubutton(r_frame, text="Filtros ▾", relief="raised", bg=self.BTN_COLOR, fg="white")
        filt_menu = tk.Menu(filt_mb, tearoff=False)
        filt_menu.add_command(label="Ministerio...", command=lambda: self._open_filter("ministry"))
        filt_menu.add_command(label="CDB...", command=lambda: self._open_filter("cdb"))
        filt_menu.add_command(label="Estado Civil...", command=lambda: self._open_filter("marital_status"))
        filt_menu.add_command(label="Estado de Membresía...", command=lambda: self._open_filter("membership_status"))
        filt_menu.add_command(label="Barrio...", command=lambda: self._open_filter("neighborhood"))
        filt_menu.add_command(label="Ocupación / Oficio...", command=lambda: self._open_filter("occupation"))
        filt_menu.add_command(label="Rango de Edad...", command=lambda: self._open_filter("age_range"))
        filt_menu.add_command(label="Género...", command=lambda: self._open_filter("gender"))
        filt_menu.add_command(label="Consolidación...", command=lambda: self._open_filter("consolidation_id"))
        filt_menu.add_separator()
        filt_menu.add_command(label="Limpiar Filtros", command=self._clear_all_filters)
        filt_mb.config(menu=filt_menu)
        filt_mb.pack(side="left", padx=2)

        # --- TREEVIEW ---
        self.tree_container = tk.Frame(self, bg=self.BG_PRIMARY)
        self.tree_container.pack(fill="both", expand=True, padx=6)
        self._create_tree()

        # --- CONTENEDOR DE DETALLES (Abajo) ---
        bottom_container = tk.Frame(self, bg=self.BG_PRIMARY)
        bottom_container.pack(fill="x", padx=6, pady=10)

        self.details_frame = tk.LabelFrame(bottom_container, text=" Ministerios en los que participa ", bg=self.BG_PRIMARY, fg=self.TEXT_DARK)
        self.details_frame.pack(side="left", fill="x", expand=True)
        
        self.details_list = tk.Listbox(self.details_frame, height=3, bg=self.BG_INPUT, relief="flat")
        self.details_list.pack(fill="x", padx=5, pady=5)

        # Botón para alternar la vista (Corregido con anchor="center")
        self.toggle_view_btn = tk.Button(
            bottom_container, 
            text="Ver Ocupación ⇄", 
            command=self._toggle_bottom_view, 
            bg=self.BTN_COLOR, 
            fg="white"
        )
        self.toggle_view_btn.pack(side="right", padx=10, anchor="center")

    def _toggle_bottom_view(self):
        """Alterna el estado de la vista inferior y refresca el contenido de la lista."""
        if self.current_view == "ministry":
            self.current_view = "occupation"
            self.details_frame.config(text=" Ocupaciones de la persona ")
            self.toggle_view_btn.config(text="Ver Ministerio ⇄")
        else:
            self.current_view = "ministry"
            self.details_frame.config(text=" Ministerios en los que participa ")
            self.toggle_view_btn.config(text="Ver Ocupación ⇄")
        
        self._on_tree_select()

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

        self.results_count_lbl.config(text=f"Resultados: {len(filtered)}")

        self.tree.delete(*self.tree.get_children())
        visible_cols = [c for c in self._all_cols if self._col_vars[c].get()]

        for p in filtered:
            values = [self._get_formatted_value(p, col) for col in visible_cols]
            self.tree.insert("", "end", iid=str(p["person_id"]), values=values)

    def _on_tree_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            self.modify_btn.config(state="disabled")
            return
        
        self.modify_btn.config(state="normal")
        self.details_list.delete(0, tk.END)
        
        try:
            pid = int(sel[0])
            
            if self.current_view == "ministry":
                mems = self.controller.get_memberships(pid) or []
                if not mems: 
                    self.details_list.insert(tk.END, "Sin asignaciones de ministerio")
                for m in mems:
                    txt = f"• {m['ministry']['name']}"
                    if m.get('area'): txt += f" / {m['area']['area']}"
                    self.details_list.insert(tk.END, txt)
                    
            elif self.current_view == "occupation":
                occups = self.controller.get_occupations(pid) or []
                if not occups:
                    self.details_list.insert(tk.END, "Sin ocupaciones registradas")
                for o in occups:
                    txt = f"• {o.get('name', 'Ocupación sin nombre')}" 
                    self.details_list.insert(tk.END, txt)
                    
        except Exception as e: 
            print(f"Error al cargar detalles inferiores: {e}")

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
                
        if col == "social_security":
            return val if val else "No tiene"
        
        if col == "consolidation_id" and val:
            obj = self.drop_helper.find_consolidation_by_id(val)
            return obj["level"] if obj else f"ID: {val}"
    
        if col == "cdb" and val:
            obj = self.drop_helper.find_cdb_by_id(val)
            return f"CDB {obj['number']}" if obj else f"ID: {val}"
        
        if col == "marital_status":
            return val if val else ""
        
        if col == "membership_status":
            return val if val else ""
        
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
            res = [p for p in res if isinstance(p.get("address"), dict) and p["address"].get("neighborhood") == f["neighborhood"]]
        
        if f["consolidation_id"]:
            res = [p for p in res if str(p.get("consolidation_id")) == str(f["consolidation_id"])]
        
        if f["occupation"]:
            try:
                # Buscamos el ID correspondiente al nombre seleccionado en la lista global de ocupaciones
                all_occs = self.config_service.get_all_occupations()
                occ_obj = next((o for o in all_occs if o.get("name") == f["occupation"]), None)
                occ_id = occ_obj.get("occupation_id") or occ_obj.get("id") if occ_obj else None
                
                if occ_id:
                    # Usamos el endpoint que reparamos anteriormente
                    people_in_occ = self.controller.get_people_by_occupation(occ_id)
                    allowed_occ_ids = {p.get("person_id") or p.get("id") for p in people_in_occ}
                    res = [p for p in res if p["person_id"] in allowed_occ_ids]
            except Exception as e:
                print(f"Error al aplicar filtro de ocupación: {e}")
                
        if f["gender"]:
            g_filter = f["gender"].lower()
            if g_filter in ("masculino", "varón", "hombre", "m"):
                res = [p for p in res if str(p.get("gender")).lower() in ("masculino", "varón", "hombre", "m")]
            elif g_filter in ("femenino", "mujer", "f"):
                res = [p for p in res if str(p.get("gender")).lower() in ("femenino", "mujer", "f")]
            else:
                res = [p for p in res if str(p.get("gender")).lower() == g_filter]

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
        
        if f["age_range"]:
            min_age, max_age = f["age_range"]
            valid_people = []
            for p in res:
                bday = p.get("birthdate")
                if not bday:
                    continue
                try:
                    if isinstance(bday, str):
                        bday_dt = datetime.strptime(bday, "%Y-%m-%d").date()
                    else:
                        bday_dt = bday
                    
                    today = datetime.now().date()
                    age = today.year - bday_dt.year - ((today.month, today.day) < (bday_dt.month, bday_dt.day))
                    
                    if min_age <= age <= max_age:
                        valid_people.append(p)
                except:
                    continue
            res = valid_people

        if f["marital_status"]:
            res = [p for p in res if p.get("marital_status") == f["marital_status"]]
        
        if f["membership_status"]:
            res = [p for p in res if p.get("membership_status") == f["membership_status"]]
            
        return res

    def _on_modify_button(self):
        """Captura el ID seleccionado y dispara el salto a la otra pestaña."""
        sel = self.tree.selection()
        if not sel:
            return
        try:
            pid = int(sel[0])
            if self._open_modify_cb:
                self._open_modify_cb(pid) 
        except Exception as e:
            print(f"Error al intentar modificar: {e}")

    def _open_filter(self, name):
        """Popup de filtro blindado contra NoneTypes."""
        win = tk.Toplevel(self)
        win.title(f"Filtrar por {name}")

        if name == "age_range":
            win.title("Filtrar por Rango de Edad")
            win.geometry("280x200")
            win.resizable(False, False)

            # Contenedor para centrar elementos
            content_frame = tk.Frame(win, bg=self.BG_PRIMARY)
            content_frame.pack(expand=True, fill="both", padx=20, pady=20)

            tk.Label(content_frame, text="Edad Mínima:", bg=self.BG_PRIMARY, fg=self.TEXT_DARK).grid(row=0, column=0, sticky="w", pady=10)
            entry_min = tk.Entry(content_frame, bg=self.BG_INPUT, fg=self.TEXT_DARK, width=8, relief="solid", bd=1)
            entry_min.insert(0, "0")
            entry_min.grid(row=0, column=1, padx=10, pady=10)

            tk.Label(content_frame, text="Edad Máxima:", bg=self.BG_PRIMARY, fg=self.TEXT_DARK).grid(row=1, column=0, sticky="w", pady=10)
            entry_max = tk.Entry(content_frame, bg=self.BG_INPUT, fg=self.TEXT_DARK, width=8, relief="solid", bd=1)
            entry_max.insert(0, "100")
            entry_max.grid(row=1, column=1, padx=10, pady=10)

            def apply_age():
                try:
                    val_min = int(entry_min.get().strip())
                    val_max = int(entry_max.get().strip())
                    if val_min > val_max:
                        messagebox.showwarning("Atención", "La edad mínima no puede ser mayor que la máxima.")
                        return
                    
                    self._active_filters["age_range"] = (val_min, val_max)
                    self.filter_info_lbl.config(text=f"Filtro: {val_min} a {val_max} años")
                    self._on_search()
                    win.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Por favor ingrese números enteros válidos.")

            tk.Button(win, text="Aplicar Filtro", command=apply_age, bg=self.BTN_COLOR, fg="white", width=15).pack(pady=(0, 15))
            return

        win.geometry("300x400")
        win.config(bg=self.BG_PRIMARY)
        
        lb = tk.Listbox(win, bg=self.BG_INPUT, fg=self.TEXT_DARK)
        lb.pack(fill="both", expand=True, padx=10, pady=10)
        
        options = []
        if name == "neighborhood":
            all_p = self.controller.search_people("")
            neighborhoods = set()
            for p in all_p:
                addr = p.get("address")
                if isinstance(addr, dict):
                    barrio = addr.get("neighborhood")
                    if barrio:
                        neighborhoods.add(barrio)
            options = sorted(list(neighborhoods))
        
        elif name == "ministry":
            self.drop_helper.refresh_all()
            options = [m["name"] for m in self.drop_helper._ministry_cache]

        elif name == "gender":
            options = ["Masculino", "Femenino"]

        elif name == "consolidation_id":
            self.drop_helper.refresh_all()
            options = [c["level"] for c in self.drop_helper._consolidation_cache]

        elif name == "occupation":
            try:
                all_occs = self.config_service.get_all_occupations()
                options = [o["name"] for o in all_occs if o.get("name")]
            except Exception as e:
                print(f"Error al cargar ocupaciones para filtro: {e}")
                options = []

        elif name == "cdb":
            self.drop_helper.refresh_all()
            options = [f"CDB {c['number']}" for c in self.drop_helper._cdb_cache]

        elif name == "membership_status":
            try:
                statuses = self.config_service.get_membership_statuses()
                options = [s["name"] for s in statuses]
            except Exception as e:
                print(f"Error al cargar membership statuses: {e}")
                options = []

        elif name == "marital_status":
            try:
                statuses = self.config_service.get_marital_statuses()
                options = [s["name"] for s in statuses]
            except Exception as e:
                print(f"Error al cargar estados civiles para filtro: {e}")
                options = ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"]
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
                
                elif name == "consolidation_id":
                    cons_obj = next((c for c in self.drop_helper._consolidation_cache if c["level"] == val), None)
                    self._active_filters[name] = cons_obj["consolidation_id"] if cons_obj else None

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