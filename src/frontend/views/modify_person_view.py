import tkinter as tk
from tkinter import ttk, messagebox
from src.frontend.views._base import BaseFrame
from src.frontend.helpers.config_dropdown_helper import ConfigDropdownHelper
from src.frontend.helpers.membership_editor_helper import MembershipEditorHelper
from tkcalendar import DateEntry # <--- Importación
from datetime import datetime

class ModifyPersonFrame(BaseFrame):
    # Pastel color scheme
    BG_PRIMARY = "#F0E6F6"
    BG_INPUT = "#FFFBF5"
    BTN_COLOR = "#7A4A97"
    TEXT_DARK = "#5A5A5A"
    
    def __init__(self, parent, controller=None, config_service=None, on_data_changed=None):
        super().__init__(parent)
        self.config(bg=self.BG_PRIMARY)
        self.controller = controller
        self.config_service = config_service
        self._on_data_changed = on_data_changed

        self.entries = {}
        self.combos = {}
        self.person_id = None
        self.drop_helper = ConfigDropdownHelper(self.config_service)
        
        self._build()

    def _build(self):
        main = tk.Frame(self, bg=self.BG_PRIMARY)
        main.pack(padx=10, pady=10, fill="both", expand=True)

        left = tk.Frame(main, bg=self.BG_PRIMARY)
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(main, bg=self.BG_PRIMARY)
        right.pack(side="right", fill="y", padx=(20, 0))

        self.entries = {}
        self.combos = {}

        fields = [
            ("person_id", "ID Persona"),
            ("first_name", "Nombre"),
            ("last_name", "Apellido"),
            ("email", "Correo"),
            ("birthdate", "Fecha de nacimiento"),
            ("gender", "Género"),
            ("dni", "DNI"),
            ("phone_number", "Teléfono"),
            ("marital_status", "Estado civil"),
            ("social_security", "Seguro Social"),
            ("street", "Calle"),
            ("neighborhood", "Barrio"),
            ("house_number", "Número de casa"),
            ("consolidation_id", "Nivel de consolidación"),
            ("cdb", "¿CDB?"),
            ("baptized", "¿Bautizado?"),
        ]

        for i, (key, label) in enumerate(fields):
            lbl = tk.Label(
                left,
                text=label,
                bg=self.BG_PRIMARY,
                fg=self.TEXT_DARK
            )

            lbl.grid(row=i, column=0, sticky="w", padx=6, pady=3)

            if key == "person_id":
                e = tk.Entry(
                    left,
                    width=40,
                    bg=self.BG_INPUT,
                    fg=self.TEXT_DARK,
                    relief="solid",
                    bd=1
                )

                e.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = e

                tk.Button(
                    left,
                    text="Cargar",
                    command=self._on_load,
                    bg=self.BTN_COLOR,
                    fg="white"
                ).grid(row=i, column=2, padx=4)

            elif key == "birthdate":
                cal = DateEntry(
                    left,
                    width=37,
                    background=self.BTN_COLOR,
                    foreground='white',
                    borderwidth=2,
                    date_pattern='yyyy-mm-dd',
                    locale='es_ES',
                    headersbackground='#E6D5F2'
                )

                cal.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = cal

            elif key in ["consolidation_id", "cdb", "baptized", "gender", "marital_status"]:
                combo = ttk.Combobox(left, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo

            else:
                e = tk.Entry(
                    left,
                    width=40,
                    bg=self.BG_INPUT,
                    fg=self.TEXT_DARK,
                    relief="solid",
                    bd=1
                )

                e.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = e

    # --- DROPDOWNS ---
        self.drop_helper.fill_consolidations(self.combos["consolidation_id"])
        self.drop_helper.fill_cdbs(self.combos["cdb"])

        statuses = [
            s["name"]
            for s in self.config_service.get_marital_statuses()
        ]

        self.combos["marital_status"]["values"] = statuses
        self.combos["baptized"]["values"] = ["Sí", "No"]
        self.combos["gender"]["values"] = ["Masculino", "Femenino"]

    # =========================================================
    # LADO DERECHO
    # =========================================================

    # --- CONTENEDOR DE MINISTERIOS ---
        membership_container = tk.Frame(right, bg=self.BG_PRIMARY)
        membership_container.grid(row=0, column=0, sticky="nw")

        self.membership_editor = MembershipEditorHelper(
            parent_frame=membership_container,
            config_service=self.config_service,
            bg_primary=self.BG_PRIMARY,
            bg_input=self.BG_INPUT,
            btn_color=self.BTN_COLOR,
            text_dark=self.TEXT_DARK
        )

        # --- CONTACTO DE EMERGENCIA ABAJO ---
        contact_frame = tk.Frame(right, bg=self.BG_PRIMARY)
        contact_frame.grid(row=1, column=0, sticky="w", pady=(20, 0))

        tk.Label(
            contact_frame,
            text="Contacto de emergencia",
            bg=self.BG_PRIMARY,
            fg=self.TEXT_DARK
        ).pack(anchor="w")

        trusted_txt = tk.Text(
            contact_frame,
            width=40,
            height=5,
            bg=self.BG_INPUT,
            fg=self.TEXT_DARK,
            relief="solid",
            bd=1,
            wrap="word"
        )

        trusted_txt.pack(anchor="w", pady=(3, 0))

        self.entries["trusted_person_info"] = trusted_txt

        # =========================================================
        # BOTONES
        # =========================================================

        btn_f = tk.Frame(left, bg=self.BG_PRIMARY)

        btn_f.grid(
            row=len(fields) + 1,
            column=0,
            columnspan=2,
            pady=20
        )

        tk.Button(
            btn_f,
            text="Guardar cambios",
            command=self._on_save,
            bg=self.BTN_COLOR,
            fg="white",
            width=18
        ).pack(side="left", padx=5)

        tk.Button(
            btn_f,
            text="Eliminar persona",
            command=self._on_delete,
            bg="#A83030",
            fg="white",
            width=18
        ).pack(side="left", padx=5)
    
    def _on_load(self):
        pid = self.entries["person_id"].get().strip()
        if not pid: return
        
        try:
            person = self.controller.get_person(int(pid))
            if not person:
                messagebox.showerror("Error", "No existe")
                return
            
            self._clear_form()
            self.person_id = person["person_id"]
            
            for key in self.entries:
                if key == "person_id": continue
                
                val = person.get(key)

                if key == "birthdate" and val:
                    try:
                        if isinstance(val, str):
                            date_obj = datetime.strptime(val, "%Y-%m-%d")
                        else:
                            date_obj = val
                        self.entries[key].set_date(date_obj)
                    except:
                        pass 
                
                elif isinstance(self.entries[key], tk.Text):
                    self.entries[key].delete("1.0", tk.END)
                    if val is not None:
                        self.entries[key].insert("1.0", str(val))
                
                elif val is not None: 
                    self.entries[key].insert(0, str(val))
            
            addr = person.get("address") or {}
            for key in ["street", "neighborhood", "house_number"]:
                val = addr.get(key)
                if val is not None: 
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, str(val))
            status_val = person.get("marital_status")
            if status_val:
                self.combos["marital_status"].set(status_val)
            self.combos["gender"].set(person.get("gender") or "")
            cons_obj = self.drop_helper.find_consolidation_by_id(person.get("consolidation_id"))
            if cons_obj: self.combos["consolidation_id"].set(cons_obj["level"])

            cdb_obj = self.drop_helper.find_cdb_by_id(person.get("cdb"))
            if cdb_obj: self.combos["cdb"].set(str(cdb_obj["number"]))

            self.combos["baptized"].set("Sí" if person.get("baptized") else "No")
            
            mems = self.controller.get_memberships(self.person_id) or []
            self.membership_editor.set_memberships(mems)

        except Exception as e:
            messagebox.showerror("Error", str(e))
    # ---------------- Guardar y Otros ----------------

    def _on_save(self):
        if not self.person_id: return
        
        payload = {}
        # CAMBIO: Extrae el texto según el tipo de widget (Text usa "1.0" a "end-1c")
        for k, widget in self.entries.items():
            if k == "person_id": 
                continue
            if isinstance(widget, tk.Text):
                val = widget.get("1.0", "end-1c").strip()
            else:
                val = widget.get() or None
            payload[k] = val if val != "" else None
        
        payload["consolidation_id"] = self.drop_helper.get_consolidation_id(self.combos["consolidation_id"].get())
        payload["cdb"] = self.drop_helper.get_cdb_id(self.combos["cdb"].get())
        payload["baptized"] = self.combos["baptized"].get() == "Sí"
        payload["gender"] = self.combos["gender"].get()
        payload["marital_status"] = self.combos["marital_status"].get()

        try:
            self.controller.update_person(self.person_id, payload)
            current_mems = self.membership_editor.memberships
            db_mems = [{"ministry_id": m["ministry_id"], "area_id": m["area_id"]} for m in current_mems]
            self.controller.update_memberships(self.person_id, db_mems)
            
            messagebox.showinfo("OK", "Actualizado correctamente")
            if self._on_data_changed: self._on_data_changed()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_delete(self):
        if not self.person_id or not messagebox.askyesno("Borrar", "¿Seguro?"): return
        try:
            self.controller.delete_person(self.person_id)
            self._clear_form()
            if self._on_data_changed: self._on_data_changed()
        except Exception as e: messagebox.showerror("Error", str(e))

    def _clear_form(self):
        """Limpia todos los campos del formulario y resetea el estado inicial."""
        for k, e in self.entries.items():
            if k == "birthdate":
                e.set_date(datetime.now()) 
            # CAMBIO: Limpieza adaptada si el campo es un tk.Text
            elif isinstance(e, tk.Text):
                e.delete("1.0", tk.END)
            else:
                e.delete(0, tk.END) 

        for c in self.combos.values(): 
            c.set("") 

        self.membership_editor.clear()
        self.person_id = None

    def refresh_dropdowns(self):
        self.drop_helper.refresh_all()
        self.drop_helper.fill_consolidations(self.combos["consolidation_id"])
        self.drop_helper.fill_cdbs(self.combos["cdb"])
        try:
            statuses = [s["name"] for s in self.config_service.get_marital_statuses()]
            self.combos["marital_status"]["values"] = statuses
        except Exception as e:
            print(f"Error al refrescar estados civiles: {e}")
        self.membership_editor.refresh_ministry_combo() 

    def load_person_by_id(self, person_id: int):
        self._clear_form()
        self.entries["person_id"].insert(0, str(person_id))
        self._on_load()