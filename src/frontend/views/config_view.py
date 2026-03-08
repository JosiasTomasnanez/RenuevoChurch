"""Configuration UI - manage ministries, areas, consolidation levels, CDB options."""
from src.frontend.views._base import BaseFrame, tk, messagebox, ttk


class ConfigurationFrame(BaseFrame):
    """Frame for managing application configuration (ministries, areas, consolidation, CDB)."""
    
    def __init__(self, master, config_service, **kwargs):
        if tk is None:
            raise RuntimeError("Tkinter not available in this environment — run GUI on a machine with Tk installed")
        super().__init__(master, **kwargs)
        self.config_service = config_service
        self._refresh_callbacks = []  # Store callbacks to notify when config changes
        self._build()
    
    def _build(self):
        """Build the configuration UI with tabbed interface."""
        # Create a notebook (tab container)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Create tabs
        self._build_ministries_tab(notebook)
        self._build_areas_tab(notebook)
        self._build_consolidation_tab(notebook)
        self._build_cdb_tab(notebook)
    
    def _build_ministries_tab(self, notebook):
        """Build the Ministries management tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Ministerios")
        
        # Input fields
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        tk.Label(input_frame, text="Nombre:").pack(side="left")
        self.ministry_name_entry = tk.Entry(input_frame, width=40)
        self.ministry_name_entry.pack(side="left", padx=6)
        
        tk.Button(input_frame, text="Agregar", command=self._add_ministry).pack(side="left", padx=3)
        tk.Button(input_frame, text="Actualizar", command=self._update_ministry).pack(side="left", padx=3)
        tk.Button(input_frame, text="Eliminar", fg="white", bg="#c0392b", command=self._delete_ministry).pack(side="left", padx=3)
        
        # List with scrollbar
        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.ministry_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=50, height=15)
        self.ministry_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.ministry_listbox.yview)
        self.ministry_listbox.bind("<<ListboxSelect>>", self._on_ministry_select)
        
        self._refresh_ministries()
    
    def _build_areas_tab(self, notebook):
        """Build the Areas management tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Áreas")
        
        # Input fields
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        tk.Label(input_frame, text="Ministerio:").pack(side="left")
        self.area_ministry_var = tk.StringVar()
        self.area_ministry_combo = ttk.Combobox(input_frame, textvariable=self.area_ministry_var, width=20, state="readonly")
        self.area_ministry_combo.pack(side="left", padx=6)
        self.area_ministry_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_areas())
        
        tk.Label(input_frame, text="Área:").pack(side="left")
        self.area_name_entry = tk.Entry(input_frame, width=30)
        self.area_name_entry.pack(side="left", padx=6)
        
        tk.Button(input_frame, text="Agregar", command=self._add_area).pack(side="left", padx=3)
        tk.Button(input_frame, text="Actualizar", command=self._update_area).pack(side="left", padx=3)
        tk.Button(input_frame, text="Eliminar", fg="white", bg="#c0392b", command=self._delete_area).pack(side="left", padx=3)
        
        # List
        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.area_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=50, height=15)
        self.area_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.area_listbox.yview)
        self.area_listbox.bind("<<ListboxSelect>>", self._on_area_select)
        
        self._refresh_ministry_combo()
        self._refresh_areas()
    
    def _build_consolidation_tab(self, notebook):
        """Build the Consolidation levels management tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Consolidación")
        
        # Input fields
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        tk.Label(input_frame, text="Nivel:").pack(side="left")
        self.consolidation_name_entry = tk.Entry(input_frame, width=40)
        self.consolidation_name_entry.pack(side="left", padx=6)
        
        tk.Button(input_frame, text="Agregar", command=self._add_consolidation).pack(side="left", padx=3)
        tk.Button(input_frame, text="Actualizar", command=self._update_consolidation).pack(side="left", padx=3)
        tk.Button(input_frame, text="Eliminar", fg="white", bg="#c0392b", command=self._delete_consolidation).pack(side="left", padx=3)
        
        # List
        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.consolidation_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=50, height=15)
        self.consolidation_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.consolidation_listbox.yview)
        self.consolidation_listbox.bind("<<ListboxSelect>>", self._on_consolidation_select)
        
        self._refresh_consolidations()
    
    def _build_cdb_tab(self, notebook):
        """Build the CDB (Casa de Bendición) configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="CDB")
        
        # Input fields
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        tk.Label(input_frame, text="Número:").pack(side="left")
        self.cdb_number_entry = tk.Entry(input_frame, width=40)
        self.cdb_number_entry.pack(side="left", padx=6)
        
        tk.Button(input_frame, text="Agregar", command=self._add_cdb).pack(side="left", padx=3)
        tk.Button(input_frame, text="Actualizar", command=self._update_cdb).pack(side="left", padx=3)
        tk.Button(input_frame, text="Eliminar", fg="white", bg="#c0392b", command=self._delete_cdb).pack(side="left", padx=3)
        
        # List with scrollbar
        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.cdb_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=50, height=15)
        self.cdb_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.cdb_listbox.yview)
        self.cdb_listbox.bind("<<ListboxSelect>>", self._on_cdb_select)
        
        self._refresh_cdb()
    
    # ========================================================================
    # Ministry operations
    # ========================================================================
    
    def _refresh_ministries(self):
        """Refresh the ministry list."""
        self.ministry_listbox.delete(0, "end")
        self._ministries = self.config_service.get_all_ministries()
        for m in self._ministries:
            self.ministry_listbox.insert("end", m["name"])
        self._refresh_ministry_combo()
        self._notify_changes()
    
    def _register_refresh_callback(self, callback):
        """Register a callback to notify when config changes."""
        if callback not in self._refresh_callbacks:
            self._refresh_callbacks.append(callback)
    
    def _notify_changes(self):
        """Call all registered refresh callbacks."""
        for cb in self._refresh_callbacks:
            try:
                cb()
            except Exception:
                pass
    
    def _refresh_ministry_combo(self):
        """Refresh the ministry dropdown in the areas tab."""
        if not hasattr(self, 'area_ministry_combo'):
            return
        ministries = self.config_service.get_all_ministries()
        names = [m["name"] for m in ministries]
        self.area_ministry_combo["values"] = names
        self._ministries_for_combo = ministries
    
    def _on_ministry_select(self, event=None):
        """Handle ministry selection."""
        sel = self.ministry_listbox.curselection()
        if sel:
            idx = sel[0]
            if idx < len(self._ministries):
                m = self._ministries[idx]
                self.ministry_name_entry.delete(0, "end")
                self.ministry_name_entry.insert(0, m["name"])
                self._selected_ministry_id = m["ministry_id"]
    
    def _add_ministry(self):
        """Add a new ministry."""
        name = self.ministry_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Ingrese un nombre de ministerio")
            return
        try:
            self.config_service.create_ministry(name)
            self.ministry_name_entry.delete(0, "end")
            self._refresh_ministries()
            messagebox.showinfo("OK", "Ministerio agregado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _update_ministry(self):
        """Update the selected ministry."""
        if not hasattr(self, "_selected_ministry_id"):
            messagebox.showerror("Error", "Seleccione un ministerio primero")
            return
        name = self.ministry_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Ingrese un nombre de ministerio")
            return
        try:
            self.config_service.update_ministry(self._selected_ministry_id, name)
            self._refresh_ministries()
            self.ministry_name_entry.delete(0, "end")
            messagebox.showinfo("OK", "Ministerio actualizado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _delete_ministry(self):
        """Delete the selected ministry."""
        if not hasattr(self, "_selected_ministry_id"):
            messagebox.showerror("Error", "Seleccione un ministerio primero")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar este ministerio y todas sus áreas?"):
            return
        try:
            self.config_service.delete_ministry(self._selected_ministry_id)
            self._refresh_ministries()
            self.ministry_name_entry.delete(0, "end")
            messagebox.showinfo("OK", "Ministerio eliminado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # ========================================================================
    # Area operations
    # ========================================================================
    
    def _refresh_areas(self):
        """Refresh the areas list for the selected ministry."""
        self.area_listbox.delete(0, "end")
        ministry_name = self.area_ministry_var.get()
        if not ministry_name:
            self._areas = []
            return
        # Find the ministry id
        ministry_id = None
        for m in self._ministries_for_combo:
            if m["name"] == ministry_name:
                ministry_id = m["ministry_id"]
                break
        if ministry_id:
            self._areas = self.config_service.get_areas_by_ministry(ministry_id)
            for a in self._areas:
                self.area_listbox.insert("end", a["area"])
        else:
            self._areas = []
    
    def _on_area_select(self, event=None):
        """Handle area selection."""
        sel = self.area_listbox.curselection()
        if sel:
            idx = sel[0]
            if idx < len(self._areas):
                a = self._areas[idx]
                self.area_name_entry.delete(0, "end")
                self.area_name_entry.insert(0, a["area"])
                self._selected_area_id = a["area_id"]
    
    def _add_area(self):
        """Add a new area."""
        ministry_name = self.area_ministry_var.get()
        if not ministry_name:
            messagebox.showerror("Error", "Seleccione un ministerio")
            return
        area = self.area_name_entry.get().strip()
        if not area:
            messagebox.showerror("Error", "Ingrese un nombre de área")
            return
        # Find ministry id
        ministry_id = None
        for m in self._ministries_for_combo:
            if m["name"] == ministry_name:
                ministry_id = m["ministry_id"]
                break
        if not ministry_id:
            messagebox.showerror("Error", "Ministerio no encontrado")
            return
        try:
            self.config_service.create_area(ministry_id, area)
            self.area_name_entry.delete(0, "end")
            self._refresh_areas()
            messagebox.showinfo("OK", "Área agregada")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _update_area(self):
        """Update the selected area."""
        if not hasattr(self, "_selected_area_id"):
            messagebox.showerror("Error", "Seleccione un área primero")
            return
        area = self.area_name_entry.get().strip()
        if not area:
            messagebox.showerror("Error", "Ingrese un nombre de área")
            return
        try:
            self.config_service.update_area(self._selected_area_id, area)
            self._refresh_areas()
            self.area_name_entry.delete(0, "end")
            messagebox.showinfo("OK", "Área actualizada")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _delete_area(self):
        """Delete the selected area."""
        if not hasattr(self, "_selected_area_id"):
            messagebox.showerror("Error", "Seleccione un área primero")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar esta área?"):
            return
        try:
            self.config_service.delete_area(self._selected_area_id)
            self._refresh_areas()
            self.area_name_entry.delete(0, "end")
            messagebox.showinfo("OK", "Área eliminada")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # ========================================================================
    # Consolidation operations
    # ========================================================================
    
    def _refresh_consolidations(self):
        """Refresh the consolidation list."""
        self.consolidation_listbox.delete(0, "end")
        self._consolidations = self.config_service.get_all_consolidations()
        for c in self._consolidations:
            self.consolidation_listbox.insert("end", c["level"])
    
    def _on_consolidation_select(self, event=None):
        """Handle consolidation selection."""
        sel = self.consolidation_listbox.curselection()
        if sel:
            idx = sel[0]
            if idx < len(self._consolidations):
                c = self._consolidations[idx]
                self.consolidation_name_entry.delete(0, "end")
                self.consolidation_name_entry.insert(0, c["level"])
                self._selected_consolidation_id = c["consolidation_id"]
    
    def _add_consolidation(self):
        """Add a new consolidation level."""
        level = self.consolidation_name_entry.get().strip()
        if not level:
            messagebox.showerror("Error", "Ingrese un nivel de consolidación")
            return
        try:
            self.config_service.create_consolidation(level)
            self.consolidation_name_entry.delete(0, "end")
            self._refresh_consolidations()
            self._notify_changes()
            messagebox.showinfo("OK", "Nivel de consolidación agregado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _update_consolidation(self):
        """Update the selected consolidation."""
        if not hasattr(self, "_selected_consolidation_id"):
            messagebox.showerror("Error", "Seleccione un nivel de consolidación primero")
            return
        level = self.consolidation_name_entry.get().strip()
        if not level:
            messagebox.showerror("Error", "Ingrese un nivel de consolidación")
            return
        try:
            self.config_service.update_consolidation(self._selected_consolidation_id, level)
            self._refresh_consolidations()
            self._notify_changes()
            self.consolidation_name_entry.delete(0, "end")
            messagebox.showinfo("OK", "Nivel de consolidación actualizado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _delete_consolidation(self):
        """Delete the selected consolidation."""
        if not hasattr(self, "_selected_consolidation_id"):
            messagebox.showerror("Error", "Seleccione un nivel de consolidación primero")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar este nivel de consolidación?"):
            return
        try:
            self.config_service.delete_consolidation(self._selected_consolidation_id)
            self._refresh_consolidations()
            self._notify_changes()
            self.consolidation_name_entry.delete(0, "end")
            messagebox.showinfo("OK", "Nivel de consolidación eliminado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # ========================================================================
    # CDB operations
    # ========================================================================
    
    def _refresh_cdb(self):
        """Refresh the CDB list."""
        self.cdb_listbox.delete(0, "end")
        self._cdb_options = self.config_service.get_all_cdb_options()
        for c in self._cdb_options:
            self.cdb_listbox.insert("end", str(c["number"]))
    
    def _on_cdb_select(self, event=None):
        """Handle CDB selection."""
        sel = self.cdb_listbox.curselection()
        if sel:
            idx = sel[0]
            if idx < len(self._cdb_options):
                c = self._cdb_options[idx]
                self.cdb_number_entry.delete(0, "end")
                self.cdb_number_entry.insert(0, str(c["number"]))
                self._selected_cdb_id = c["cdb_id"]
    
    def _add_cdb(self):
        """Add a new CDB house."""
        try:
            number_str = self.cdb_number_entry.get().strip()
            if not number_str:
                messagebox.showerror("Error", "Ingrese un número de CDB")
                return
            number = int(number_str)
            self.config_service.create_cdb(number)
            self.cdb_number_entry.delete(0, "end")
            self._refresh_cdb()
            self._notify_changes()
            messagebox.showinfo("OK", "CDB agregado")
        except ValueError:
            messagebox.showerror("Error", "El número de CDB debe ser un entero")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _update_cdb(self):
        """Update the selected CDB."""
        if not hasattr(self, "_selected_cdb_id"):
            messagebox.showerror("Error", "Seleccione un CDB primero")
            return
        try:
            number_str = self.cdb_number_entry.get().strip()
            if not number_str:
                messagebox.showerror("Error", "Ingrese un número de CDB")
                return
            number = int(number_str)
            self.config_service.update_cdb(self._selected_cdb_id, number)
            self._refresh_cdb()
            self._notify_changes()
            self.cdb_number_entry.delete(0, "end")
            messagebox.showinfo("OK", "CDB actualizado")
        except ValueError:
            messagebox.showerror("Error", "El número de CDB debe ser un entero")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _delete_cdb(self):
        """Delete the selected CDB."""
        if not hasattr(self, "_selected_cdb_id"):
            messagebox.showerror("Error", "Seleccione un CDB primero")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar esta CDB?"):
            return
        try:
            self.config_service.delete_cdb(self._selected_cdb_id)
            self._refresh_cdb()
            self._notify_changes()
            self.cdb_number_entry.delete(0, "end")
            messagebox.showinfo("OK", "CDB eliminado")
        except Exception as e:
            messagebox.showerror("Error", str(e))


__all__ = ["ConfigurationFrame"]
