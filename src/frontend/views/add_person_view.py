from src.frontend.views._base import BaseFrame, tk, messagebox, ttk
from src.frontend.helpers.config_dropdown_helper import ConfigDropdownHelper
from src.frontend.helpers.membership_editor_helper import MembershipEditorHelper # <--- NUEVA IMPORTACIÓN
from tkcalendar import DateEntry

class AddPersonFrame(BaseFrame):
    BG_PRIMARY = "#F0E6F6"
    BG_INPUT = "#FFFBF5"
    BTN_COLOR = "#7A4A97"
    TEXT_DARK = "#5A5A5A"
    
    def __init__(self, master, controller, config_service=None, open_modify_callback=None,on_data_changed=None, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.config_service = config_service
        self._on_data_changed = on_data_changed
        self._open_modify_cb = open_modify_callback
        self.config(bg=self.BG_PRIMARY)
        
        self.drop_helper = ConfigDropdownHelper(self.config_service)
        # Ya no necesitamos self._memberships manual, lo tiene el helper
        
        self._build()

    def _build(self):
        self.entries = {}
        self.combos = {}

        main = tk.Frame(self, bg=self.BG_PRIMARY)
        main.pack(fill="both", expand=True, padx=6, pady=6)

        left = tk.Frame(main, bg=self.BG_PRIMARY)
        left.grid(row=0, column=0, sticky="nw")

        right = tk.Frame(main, bg=self.BG_PRIMARY)
        right.grid(row=0, column=1, sticky="ne", padx=(20, 0))

        # --- LADO IZQUIERDO (IGUAL QUE ANTES) ---
        fields = [
            ("first_name", "Nombre *"), ("last_name", "Apellido *"),
            ("email", "Correo"), ("birthdate", "Fecha de nacimiento"),
            ("gender", "Género"),
            ("dni", "DNI"), ("phone_number", "Teléfono"),
            ("marital_status", "Estado civil"), ("social_security", "Seguro Social"),
            ("street", "Calle"), ("neighborhood", "Barrio"),
            ("house_number", "Número de casa"),
            ("consolidation_id", "Nivel de consolidación"),
            ("cdb", "¿CDB?"), ("baptized", "¿Bautizado?"),
        ]

        for i, (key, label) in enumerate(fields):
            tk.Label(left, text=label, bg=self.BG_PRIMARY, fg=self.TEXT_DARK).grid(row=i, column=0, sticky="w", padx=6, pady=3)
            
            if key in ["consolidation_id", "cdb", "baptized", "gender","marital_status"]:
                combo = ttk.Combobox(left, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo
            elif key == "birthdate":
                cal = DateEntry(
                    left, 
                    width=37, 
                    background=self.BTN_COLOR,
                    foreground='white', 
                    borderwidth=2,
                    year=2000, 
                    date_pattern='yyyy-mm-dd', # Formato que entiende tu BD
                    locale='es_ES',            # Meses en español
                    headersbackground='#E6D5F2'
                )
                cal.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = cal # Guardamos el widget en entries para que _on_submit lo lea igual
            
            else:
                ent = tk.Entry(left, width=40, bg=self.BG_INPUT, fg=self.TEXT_DARK, relief="solid", bd=1)
                ent.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = ent

        self.drop_helper.fill_consolidations(self.combos["consolidation_id"])
        self.drop_helper.fill_cdbs(self.combos["cdb"])
        self.drop_helper.fill_marital_statuses(self.combos["marital_status"])
        
        self.combos["gender"]["values"] = ["Masculino", "Femenino"] 

        self.combos["baptized"]["values"] = ["Sí", "No"]
        self.combos["baptized"].set("No") 

        tk.Button(left, text="Agregar persona", command=self._on_submit, bg=self.BTN_COLOR, fg="white").grid(row=len(fields), column=0, columnspan=2, pady=(12, 0))

        self.membership_editor = MembershipEditorHelper(
            parent_frame=right,
            config_service=self.config_service,
            bg_primary=self.BG_PRIMARY,
            bg_input=self.BG_INPUT,
            btn_color=self.BTN_COLOR,
            text_dark=self.TEXT_DARK
        )

    def _on_submit(self):
        payload = {k: (v.get() or None) for k, v in self.entries.items()}
        
        if not payload.get("first_name") or not payload.get("last_name"):
            messagebox.showerror("Error", "Nombre y Apellido son obligatorios")
            return

        payload["gender"] = self.combos["gender"].get() 
        payload["baptized"] = self.combos["baptized"].get() == "Sí"
        payload["marital_status"] = self.combos["marital_status"].get()
        payload["consolidation_id"] = self.drop_helper.get_consolidation_id(self.combos["consolidation_id"].get())
        payload["cdb"] = self.drop_helper.get_cdb_id(self.combos["cdb"].get())


        try:
            person_id = self.controller.create_person(payload)
            current_mems = self.membership_editor.memberships
            if current_mems:
                db_mems = [{"ministry_id": m["ministry_id"], "area_id": m["area_id"]} for m in current_mems]
                self.controller.update_memberships(person_id, db_mems)
            
            messagebox.showinfo("OK", "Persona creada exitosamente")
            self._clear_form()
            if self._on_data_changed:
                self._on_data_changed()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _clear_form(self):
        for e in self.entries.values(): e.delete(0, "end")
        for c in self.combos.values(): c.set("")
        self.combos["baptized"].set("No")
        self.combos["gender"].set("Masculino")
        # Limpiar el helper
        self.membership_editor.clear()

    def refresh_dropdowns(self):
        """Llamado cuando cambia la configuración global"""
        self.drop_helper.refresh_all()
        self.drop_helper.fill_consolidations(self.combos["consolidation_id"])
        self.drop_helper.fill_cdbs(self.combos["cdb"])
        self.drop_helper.fill_marital_statuses(self.combos["marital_status"])
        self.membership_editor.refresh_ministry_combo()