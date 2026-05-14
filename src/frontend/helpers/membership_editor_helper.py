"""
Helper para la gestión de membresías (ministerios y áreas).
Centraliza la lógica de la UI y la gestión de la lista de asignaciones.
"""
import tkinter as tk
from tkinter import ttk, messagebox

class MembershipEditorHelper:
    def __init__(self, parent_frame, config_service=None, bg_primary="#F0E6F6",
                 bg_input="#FFFBF5", btn_color="#7A4A97", text_dark="#5A5A5A"):
        
        self.parent_frame = parent_frame
        self.config_service = config_service
        
        # Colores consistentes con tu App
        self.colors = {
            "bg": bg_primary,
            "input": bg_input,
            "btn": btn_color,
            "text": text_dark
        }

        self._ministry_options = []  # Lista de dicts del backend
        self._area_options = []      # Lista de dicts del backend
        self._memberships = []       # Lo que el usuario va agregando

        self._build_ui()

    def _build_ui(self):
        """Construye los widgets dentro del frame padre."""
        # Título interno
        tk.Label(self.parent_frame, text="Ministerios", 
                 bg=self.colors["bg"], fg=self.colors["text"], 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Contenedor de selección
        controls = tk.Frame(self.parent_frame, bg=self.colors["bg"])
        controls.grid(row=1, column=0, sticky="we")

        self._min_combo = ttk.Combobox(controls, width=18, state="readonly")
        self._min_combo.grid(row=0, column=0, padx=2)
        self._min_combo.bind("<<ComboboxSelected>>", self._on_ministry_change)

        self._area_combo = ttk.Combobox(controls, width=18, state="readonly")
        self._area_combo.grid(row=0, column=1, padx=2)

        tk.Button(controls, text="Agregar", command=self._on_add, 
                  bg=self.colors["btn"], fg="white", width=8,relief="flat",pady=2).grid(row=0, column=2, padx=5)

        # Listbox de membresías actuales
        self._listbox = tk.Listbox(self.parent_frame, height=5, bg=self.colors["input"], 
                                   fg=self.colors["text"], relief="flat", bd=1)
        self._listbox.grid(row=2, column=0, sticky="we", pady=5)

        tk.Button(self.parent_frame, text="Quitar seleccionada", command=self._on_remove, 
                  bg="#A83030", fg="white", font=("Arial", 8)).grid(row=3, column=0, sticky="w")

        self.refresh_ministry_combo()

    # --- Lógica de Datos ---

    def refresh_ministry_combo(self):
        """Carga o recarga los ministerios desde el config_service."""
        try:
            self._ministry_options = self.config_service.get_all_ministries()
            names = [m["name"] for m in self._ministry_options]
            self._min_combo["values"] = names
        except Exception as e:
            print(f"Error cargando ministerios en helper: {e}")

    def _on_ministry_change(self, event=None):
        """Carga las áreas según el ministerio elegido."""
        idx = self._min_combo.current()
        if idx < 0: return
        
        m_id = self._ministry_options[idx]["ministry_id"]
        try:
            self._area_options = self.config_service.get_areas_by_ministry(m_id)
            names = [a["area"] for a in self._area_options]
            self._area_combo["values"] = names
            self._area_combo.set("") # Limpiar selección previa
        except:
            self._area_combo["values"] = []

    def _on_add(self):
        """Agrega la combinación actual a la lista temporal."""
        m_idx = self._min_combo.current()
        if m_idx < 0:
            messagebox.showwarning("Atención", "Seleccione al menos un ministerio.")
            return

        ministry = self._ministry_options[m_idx]
        a_idx = self._area_combo.current()
        
        area_id = None
        area_name = ""
        
        if a_idx >= 0:
            area = self._area_options[a_idx]
            area_id = area["area_id"]
            area_name = area["area"]

        # Evitar duplicados exactos
        for existing in self._memberships:
            if existing["ministry_id"] == ministry["ministry_id"] and existing["area_id"] == area_id:
                return

        self._memberships.append({
            "ministry_id": ministry["ministry_id"],
            "ministry_name": ministry["name"],
            "area_id": area_id,
            "area_name": area_name
        })
        self._update_listbox()

    def _on_remove(self):
        """Elimina el item seleccionado de la lista."""
        sel = self._listbox.curselection()
        if sel:
            self._memberships.pop(sel[0])
            self._update_listbox()

    def _update_listbox(self):
        """Sincroniza lo visual con la lista interna."""
        self._listbox.delete(0, tk.END)
        for m in self._memberships:
            txt = m["ministry_name"]
            if m["area_name"]:
                txt += f" | {m['area_name']}"
            self._listbox.insert(tk.END, txt)

    # --- API Pública para las Vistas ---

    @property
    def memberships(self):
        """Retorna la lista de diccionarios lista para el backend."""
        return self._memberships

    def set_memberships(self, membership_data):
        """
        Carga membresías existentes (usado al cargar una persona).
        'membership_data' debe ser la lista que viene del backend.
        """
        self.clear()
        for item in membership_data:
            # Normalizamos porque el backend a veces trae objetos anidados
            m_name = item.get("ministry", {}).get("name") if isinstance(item.get("ministry"), dict) else item.get("ministry_name")
            a_name = item.get("area", {}).get("area") if isinstance(item.get("area"), dict) else item.get("area_name")
            
            self._memberships.append({
                "ministry_id": item.get("ministry_id"),
                "ministry_name": m_name or "Minst.",
                "area_id": item.get("area_id"),
                "area_name": a_name or ""
            })
        self._update_listbox()

    def clear(self):
        """Limpia todo el editor."""
        self._memberships = []
        self._min_combo.set("")
        self._area_combo.set("")
        self._listbox.delete(0, tk.END)