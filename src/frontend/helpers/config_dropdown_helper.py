"""Helper for managing configuration dropdowns with UI synchronization and caching."""
from typing import Optional, Dict, List

class ConfigDropdownHelper:
    def __init__(self, config_service):
        self.config_service = config_service
        
        # Cachés internas para no pegarle a la DB en cada click
        self._ministry_cache = []
        self._consolidation_cache = []
        self._cdb_cache = []
        self._marital_cache = []
        self._membership_cache = []

  
    def refresh_all(self):
        """Fuerza la recarga de todos los datos desde el service."""
        try:
            self._ministry_cache = self.config_service.get_all_ministries()
            self._consolidation_cache = self.config_service.get_all_consolidations()
            self._cdb_cache = self.config_service.get_all_cdb_options()
            self._marital_cache = self.config_service.get_marital_statuses()
            self._membership_cache = self.config_service.get_membership_statuses()
          
                
        except Exception:
            self._ministry_cache = []
            self._consolidation_cache = []
            self._cdb_cache = []
            self._marital_cache = []

    # --- Métodos para refrescar caches individuales (para refresh dirigido) ---
    def refresh_ministry_cache(self):
        try:
            self._ministry_cache = self.config_service.get_all_ministries()
        except Exception:
            self._ministry_cache = []

    def refresh_consolidation_cache(self):
        try:
            self._consolidation_cache = self.config_service.get_all_consolidations()
        except Exception:
            self._consolidation_cache = []

    def refresh_cdb_cache(self):
        try:
            self._cdb_cache = self.config_service.get_all_cdb_options()
        except Exception:
            self._cdb_cache = []

    def refresh_marital_cache(self):
        try:
            self._marital_cache = self.config_service.get_marital_statuses()
        except Exception:
            self._marital_cache = []

    def refresh_membership_cache(self):
        try:
            self._membership_cache = self.config_service.get_membership_statuses()
        except Exception:
            self._membership_cache = []

    # --- MÉTODOS PARA LLENAR COMBOS (UI) ---
    def fill_ministries(self, combo):
        if not self._ministry_cache: self._ministry_cache = self.config_service.get_all_ministries()
        combo["values"] = [m["name"] for m in self._ministry_cache]

    def fill_consolidations(self, combo):
        if not self._consolidation_cache: self._consolidation_cache = self.config_service.get_all_consolidations()
        combo["values"] = [c["level"] for c in self._consolidation_cache]

    def fill_cdbs(self, combo):
        if not self._cdb_cache: self._cdb_cache = self.config_service.get_all_cdb_options()
        # Convertimos a string porque los números de CDB suelen venir como int
        combo["values"] = [str(c["number"]) for c in self._cdb_cache]

    def bind_ministry_area(self, ministry_combo, area_combo):
        """Sincroniza el combo de áreas basado en el ministerio elegido."""
        def on_change(event):
            m_name = ministry_combo.get()
            m_id = self.get_ministry_id(m_name)
            
            if m_id:
                areas = self.config_service.get_areas_by_ministry(m_id)
                area_combo.config(state="readonly")
                area_combo["values"] = [a["area"] for a in areas]
            else:
                area_combo.config(state="disabled")
                area_combo["values"] = []
            area_combo.set("")

        ministry_combo.bind("<<ComboboxSelected>>", on_change)

    # --- MÉTODOS PARA OBTENER IDs (Para el Submit) ---
    def get_ministry_id(self, name: str) -> Optional[int]:
        for m in self._ministry_cache:
            if m["name"] == name: return m["ministry_id"]
        return None

    def get_consolidation_id(self, level_name: str) -> Optional[int]:
        for c in self._consolidation_cache:
            if c["level"] == level_name: return c["consolidation_id"]
        return None

    def get_cdb_id(self, cdb_number: str) -> Optional[int]:
        # Como en el combo son strings, comparamos convirtiendo
        for c in self._cdb_cache:
            if str(c["number"]) == cdb_number: return c["cdb_id"]
        return None
    
    # --- MÉTODOS DE BÚSQUEDA INVERSA (Para Modificar/Cargar) ---
    def find_consolidation_by_id(self, consolidation_id: int) -> Optional[Dict]:
        if not self._consolidation_cache: self._consolidation_cache = self.config_service.get_all_consolidations()
        for c in self._consolidation_cache:
            if c.get("consolidation_id") == consolidation_id:
                return c
        return None

    def find_cdb_by_id(self, cdb_id: int) -> Optional[Dict]:
        if not self._cdb_cache: self._cdb_cache = self.config_service.get_all_cdb_options()
        for c in self._cdb_cache:
            if c.get("cdb_id") == cdb_id:
                return c
        return None

    def find_ministry_by_id(self, ministry_id: int) -> Optional[Dict]:
        if not self._ministry_cache: self._ministry_cache = self.config_service.get_all_ministries()
        for m in self._ministry_cache:
            if m.get("ministry_id") == ministry_id:
                return m
        return None
    
    def fill_marital_statuses(self, combo):
        """Llena el combo con los textos de estado civil desde el ConfigService."""
        try:
            if not self._marital_cache:
                self._marital_cache = self.config_service.get_marital_statuses()
            
            combo["values"] = [m["name"] for m in self._marital_cache]
        except Exception as e:
            print(f"Error al llenar estados civiles: {e}")
            combo["values"] = ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"]
    
    def fill_membership_statuses(self, combo):
        if not self._membership_cache:
            self._membership_cache = self.config_service.get_membership_statuses()

        combo["values"] = [m["name"] for m in self._membership_cache]

    def get_membership_status_id(self, name: str):
        for m in self._membership_cache:
            if m["name"] == name:
                return m["id"]
        return None