"""Configuration UI - manage ministries, areas, consolidation levels, CDB options."""
from src.frontend.views._base import BaseFrame, tk, messagebox, ttk
from src.frontend.helpers.config_table_helper import ConfigTableHelper
from src.frontend.utils.config_manager import ConfigManager

class ConfigurationFrame(BaseFrame):
    """Frame for managing application configuration (ministries, areas, consolidation, CDB, occupations)."""
    
    def __init__(self, master, config_service, **kwargs):
        super().__init__(master, **kwargs)
        self.config_service = config_service
        self._refresh_callbacks = []
        self._ministries_data = []
    
        self._build()
    
    def _build(self):
        """Build the configuration UI with tabbed interface."""
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=6, pady=6)
        
        self._build_ministries_tab(notebook)
        self._build_areas_tab(notebook)
        self._build_consolidation_tab(notebook)
        self._build_cdb_tab(notebook)
        self._build_marital_status_tab(notebook)
        self._build_membership_status_tab(notebook)
        self._build_occupations_tab(notebook) # <-- Agregada a la botonera general

    def _on_config_changed(self):
        """Se llama cuando cualquier tabla cambia para refrescar combos y avisar a otros."""
        self._refresh_ministry_combo()
        for cb in self._refresh_callbacks:
            try: cb()
            except: pass

    def _register_refresh_callback(self, callback):
        if callback not in self._refresh_callbacks:
            self._refresh_callbacks.append(callback)

    def _build_occupations_tab(self, notebook):
        """Pestaña para gestionar las Ocupaciones de forma idéntica al resto de enums."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Ocupaciones")
        
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        tk.Label(input_frame, text="Nombre:").pack(side="left")
        entry = tk.Entry(input_frame, width=40)
        entry.pack(side="left", padx=6)
        
        listbox = tk.Listbox(frame, width=50, height=15)
        listbox.pack(padx=6, pady=6, fill="both", expand=True)

        self.occupation_helper = ConfigTableHelper(
            label="Ocupación",
            entry_widget=entry,
            listbox_widget=listbox,
            on_get_items=self.config_service.get_all_occupations,
            on_add=self.config_service.create_occupation,
            on_update=lambda id, val: None,
            on_delete=self.config_service.delete_occupation,
            display_key="name",
            item_id_key="occupation_id", # <-- CAMBIAR ACÁ: de "id" a "occupation_id"
            on_change=lambda: ConfigManager.get_instance().publish("occupations.updated")
        )

        tk.Button(input_frame, text="Agregar", command=self.occupation_helper.add).pack(side="left")
        tk.Button(input_frame, text="Eliminar", command=self.occupation_helper.delete, bg="#c0392b", fg="white").pack(side="left")
        
        self.occupation_helper.refresh_list()

    def _build_marital_status_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Estado Civil")
        
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        tk.Label(input_frame, text="Nombre:").pack(side="left")
        entry = tk.Entry(input_frame, width=40)
        entry.pack(side="left", padx=6)
        
        listbox = tk.Listbox(frame, width=50, height=15)
        listbox.pack(padx=6, pady=6, fill="both", expand=True)

        # Usamos el mismo helper de tablas que usas para Ministerios
        self.marital_helper = ConfigTableHelper(
            label="Estado Civil",
            entry_widget=entry,
            listbox_widget=listbox,
            on_get_items=self.config_service.get_marital_statuses,
            on_add=self.config_service.create_marital_status,
            on_update=lambda id, val: None, # Opcional: no pusimos update en el repo
            on_delete=self.config_service.delete_marital_status,
            display_key="name",
            item_id_key="id",
            on_change=lambda: ConfigManager.get_instance().publish("marital.updated")
        )

        tk.Button(input_frame, text="Agregar", command=self.marital_helper.add).pack(side="left")
        tk.Button(input_frame, text="Eliminar", command=self.marital_helper.delete, bg="#c0392b", fg="white").pack(side="left")
        
        self.marital_helper.refresh_list()

    def _build_membership_status_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Estado Membresía")

        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)

        tk.Label(input_frame, text="Nombre:").pack(side="left")
        entry = tk.Entry(input_frame, width=40)
        entry.pack(side="left", padx=6)

        listbox = tk.Listbox(frame, width=50, height=15)
        listbox.pack(padx=6, pady=6, fill="both", expand=True)

        self.membership_helper = ConfigTableHelper(
            label="Estado Membresía",
            entry_widget=entry,
            listbox_widget=listbox,
            on_get_items=self.config_service.get_membership_statuses,
            on_add=self.config_service.create_membership_status,
            on_update=lambda id, val: None,  # igual que marital
            on_delete=self.config_service.delete_membership_status,
            display_key="name",
            item_id_key="id",
            on_change=lambda: ConfigManager.get_instance().publish("membership.updated")
        )

        tk.Button(input_frame, text="Agregar", command=self.membership_helper.add).pack(side="left")
        tk.Button(input_frame, text="Eliminar", command=self.membership_helper.delete, bg="#c0392b", fg="white").pack(side="left")

        self.membership_helper.refresh_list()

    def _build_ministries_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Ministerios")
        
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        tk.Label(input_frame, text="Nombre:").pack(side="left")
        entry = tk.Entry(input_frame, width=40)
        entry.pack(side="left", padx=6)
        
        listbox = tk.Listbox(frame, width=50, height=15)
        listbox.pack(padx=6, pady=6, fill="both", expand=True)

        self.ministry_helper = ConfigTableHelper(
            label="Ministerio",
            entry_widget=entry,
            listbox_widget=listbox,
            on_get_items=self.config_service.get_all_ministries,
            on_add=self.config_service.create_ministry,
            on_update=self.config_service.update_ministry,
            on_delete=self.config_service.delete_ministry,
            display_key="name",
            item_id_key="ministry_id",
            on_change=lambda: (self._refresh_ministry_combo() or ConfigManager.get_instance().publish("ministries.updated"))
        )

        tk.Button(input_frame, text="Agregar", command=self.ministry_helper.add).pack(side="left", padx=2)
        tk.Button(input_frame, text="Actualizar", command=self.ministry_helper.update).pack(side="left", padx=2)
        tk.Button(input_frame, text="Eliminar", command=self.ministry_helper.delete, bg="#c0392b", fg="white").pack(side="left", padx=2)
        
        self.ministry_helper.refresh_list()

    def _build_areas_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Áreas")
        
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        tk.Label(input_frame, text="Ministerio:").pack(side="left")
        self.area_ministry_var = tk.StringVar()
        self.area_ministry_combo = ttk.Combobox(input_frame, textvariable=self.area_ministry_var, state="readonly")
        self.area_ministry_combo.pack(side="left", padx=6)
        
        tk.Label(input_frame, text="Área:").pack(side="left")
        entry = tk.Entry(input_frame, width=30)
        entry.pack(side="left", padx=6)
        
        listbox = tk.Listbox(frame, width=50, height=15)
        listbox.pack(padx=6, pady=6, fill="both", expand=True)

        self.area_helper = ConfigTableHelper(
            label="Área",
            entry_widget=entry,
            listbox_widget=listbox,
            on_get_items=self._get_areas_filtered, # Función puente
            on_add=self.config_service.create_area,
            on_update=self.config_service.update_area,
            on_delete=self.config_service.delete_area,
            display_key="area",
            item_id_key="area_id",
            on_change=lambda: ConfigManager.get_instance().publish("areas.updated")
        )

        tk.Button(input_frame, text="Agregar", command=self._add_area_wrapper).pack(side="left")
        tk.Button(input_frame, text="Actualizar", command=self.area_helper.update).pack(side="left")
        tk.Button(input_frame, text="Eliminar", command=self.area_helper.delete, bg="#c0392b", fg="white").pack(side="left")

        self.area_ministry_combo.bind("<<ComboboxSelected>>", lambda e: self.area_helper.refresh_list())
        self._refresh_ministry_combo()

    def _get_areas_filtered(self):
        m_id = self._get_current_ministry_id()
        return self.config_service.get_areas_by_ministry(m_id) if m_id else []

    def _add_area_wrapper(self):
        m_id = self._get_current_ministry_id()
        if not m_id:
            messagebox.showerror("Error", "Seleccione un ministerio")
            return
    
        area_name = self.area_helper.entry_widget.get().strip()
    
        if not area_name:
            messagebox.showerror("Error", "Ingrese un nombre de área")
            return

        try:
            self.config_service.create_area(m_id, area_name)
            self.area_helper.entry_widget.delete(0, "end")
            self.area_helper.refresh_list()
            messagebox.showinfo("OK", "Área agregada correctamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _get_current_ministry_id(self):
        m_name = self.area_ministry_var.get()
        for m in self._ministries_data: # <--- Más limpio
            if m["name"] == m_name: return m["ministry_id"]
        return None

    def _refresh_ministry_combo(self):
        self._ministries_data = self.config_service.get_all_ministries()
        names = [m["name"] for m in self._ministries_data]
        self.area_ministry_combo["values"] = names

    def _build_consolidation_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Consolidación")
        
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        entry = tk.Entry(input_frame, width=40)
        entry.pack(side="left", padx=6)
        
        listbox = tk.Listbox(frame, width=50, height=15)
        listbox.pack(fill="both", expand=True, padx=6, pady=6)

        helper = ConfigTableHelper(
            label="Nivel",
            entry_widget=entry,
            listbox_widget=listbox,
            on_get_items=self.config_service.get_all_consolidations,
            on_add=self.config_service.create_consolidation,
            on_update=self.config_service.update_consolidation,
            on_delete=self.config_service.delete_consolidation,
            display_key="level",
            item_id_key="consolidation_id",
            on_change=lambda: ConfigManager.get_instance().publish("consolidation.updated")
        )

        tk.Button(input_frame, text="Agregar", command=helper.add).pack(side="left")
        tk.Button(input_frame, text="Actualizar", command=helper.update).pack(side="left")
        tk.Button(input_frame, text="Eliminar", command=helper.delete, bg="#c0392b", fg="white").pack(side="left")
        helper.refresh_list()

    def _build_cdb_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="CDB")
        
        input_frame = tk.Frame(frame)
        input_frame.pack(fill="x", padx=6, pady=6)
        
        entry = tk.Entry(input_frame, width=40)
        entry.pack(side="left", padx=6)
        
        listbox = tk.Listbox(frame, width=50, height=15)
        listbox.pack(fill="both", expand=True, padx=6, pady=6)

        helper = ConfigTableHelper(
            label="CDB",
            entry_widget=entry,
            listbox_widget=listbox,
            on_get_items=self.config_service.get_all_cdb_options,
            on_add=self.config_service.create_cdb,
            on_update=self.config_service.update_cdb,
            on_delete=self.config_service.delete_cdb,
            display_key="number",
            item_id_key="cdb_id",
            on_change=lambda: ConfigManager.get_instance().publish("cdb.updated")
        )

        tk.Button(input_frame, text="Agregar", command=helper.add).pack(side="left")
        tk.Button(input_frame, text="Actualizar", command=helper.update).pack(side="left")
        tk.Button(input_frame, text="Eliminar", command=helper.delete, bg="#c0392b", fg="white").pack(side="left")
        helper.refresh_list()

__all__ = ["ConfigurationFrame"]