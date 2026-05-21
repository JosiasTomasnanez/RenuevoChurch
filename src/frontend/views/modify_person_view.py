import tkinter as tk
from tkinter import ttk, messagebox
from src.frontend.views._base import BaseFrame
from src.frontend.helpers.config_dropdown_helper import ConfigDropdownHelper
from src.frontend.helpers.membership_editor_helper import MembershipEditorHelper
from tkcalendar import DateEntry 
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
        self._selected_occupations = [] # Lista temporal en memoria
        
        self._build()

    def _build(self):
        main = tk.Frame(self, bg=self.BG_PRIMARY)
        main.pack(padx=10, pady=10, fill="both", expand=True)

        left = tk.Frame(main, bg=self.BG_PRIMARY)
        left.pack(side="left", fill="both")

        right = tk.Frame(main, bg=self.BG_PRIMARY)
        right.pack(side="left", fill="y", padx=(10, 0))

        self.entries = {}
        self.combos = {}

        # =========================================================
        # HEADER (ID + CARGAR)
        # =========================================================
        header = tk.Frame(left, bg=self.BG_PRIMARY)
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        tk.Label(
            header,
            text="ID Persona",
            bg=self.BG_PRIMARY,
            fg=self.TEXT_DARK
        ).pack(side="left", padx=(0, 5))

        self.entries["person_id"] = tk.Entry(
            header,
            width=10,
            bg=self.BG_INPUT,
            fg=self.TEXT_DARK,
            relief="solid",
            bd=1
        )
        self.entries["person_id"].pack(side="left")

        tk.Button(
            header,
            text="Cargar",
            command=self._on_load,
            bg=self.BTN_COLOR,
            fg="white"
        ).pack(side="left", padx=5)

        # =========================================================
        # CAMPOS
        # =========================================================
        fields = [
            ("first_name", "Nombre"),
            ("last_name", "Apellido"),
            ("email", "Correo"),
            ("birthdate", "Fecha de nacimiento"),
            ("gender", "Género"),
            ("dni", "DNI"),
            ("phone_number", "Teléfono"),
            ("marital_status", "Estado civil"),
            ("membership_status", "Estado membresía"), 
            ("social_security", "Seguro Social"),
            ("street", "Calle"),
            ("neighborhood", "Barrio"),
            ("house_number", "Número de casa"),
            ("consolidation_id", "Nivel de consolidación"),
            ("cdb", "¿CDB?"),
            ("baptized", "¿Bautizado?"),
        ]

        for i, (key, label) in enumerate(fields, start=1):
            tk.Label(
                left,
                text=label,
                bg=self.BG_PRIMARY,
                fg=self.TEXT_DARK
            ).grid(row=i, column=0, sticky="w", padx=6, pady=3)

            # -------------------------
            # COMBOS
            # -------------------------
            if key in ["consolidation_id", "cdb", "baptized", "gender", "marital_status", "membership_status"]:
                combo = ttk.Combobox(left, width=37, state="readonly")
                combo.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.combos[key] = combo

            # -------------------------
            # DATE
            # -------------------------
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

            # -------------------------
            # INPUTS
            # -------------------------
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

        # =========================================================
        # DROPDOWNS
        # =========================================================
        self.drop_helper.fill_consolidations(self.combos["consolidation_id"])
        self.drop_helper.fill_cdbs(self.combos["cdb"])

        statuses = [s["name"] for s in self.config_service.get_marital_statuses()]
        self.combos["marital_status"]["values"] = statuses

        ms = [m["name"] for m in self.config_service.get_membership_statuses()]
        self.combos["membership_status"]["values"] = ms

        self.combos["baptized"]["values"] = ["Sí", "No"]
        self.combos["gender"]["values"] = ["Masculino", "Femenino"]

        # =========================================================
        # LADO DERECHO
        # =========================================================

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

        # -------------------------
        # CONTACTO EMERGENCIA
        # -------------------------
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

        # ---------------------------------------------------------
        # NUEVO: SECCIÓN OCUPACIONES / OFICIOS (IGUAL A ADD PERSON)
        # ---------------------------------------------------------
        occupations_frame = tk.Frame(right, bg=self.BG_PRIMARY)
        occupations_frame.grid(row=2, column=0, sticky="w", pady=(15, 0))

        tk.Label(
            occupations_frame,
            text="Ocupaciones / Oficios",
            bg=self.BG_PRIMARY,
            fg=self.TEXT_DARK,
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="w", pady=(0, 3))

        add_occ_row = tk.Frame(occupations_frame, bg=self.BG_PRIMARY)
        add_occ_row.pack(fill="x", anchor="w")

        self.occ_combo_var = tk.StringVar()
        self.occ_combobox = ttk.Combobox(add_occ_row, textvariable=self.occ_combo_var, width=25, state="readonly")
        self.occ_combobox.pack(side="left", padx=(0, 6))

        tk.Button(
            add_occ_row,
            text="Agregar",
            command=self._add_occupation_to_list,
            bg=self.BTN_COLOR,
            fg="white",
            padx=5
        ).pack(side="left")

        self.occupations_listbox = tk.Listbox(
            occupations_frame,
            width=40,
            height=4,
            bg=self.BG_INPUT,
            fg=self.TEXT_DARK,
            relief="solid",
            bd=1
        )
        self.occupations_listbox.pack(anchor="w", pady=5)

        tk.Button(
            occupations_frame,
            text="Quitar seleccionado",
            command=self._remove_occupation_from_list,
            bg="#c0392b",
            fg="white",
            padx=5
        ).pack(anchor="w")
        
        self._refresh_occupations_combo()

        # =========================================================
        # BOTONES
        # =========================================================
        btn_f = tk.Frame(left, bg=self.BG_PRIMARY)
        btn_f.grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

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

    # ---------------- Lógica del Combo de Ocupaciones ----------------

    def _refresh_occupations_combo(self):
        try:
            self._global_occupations = self.config_service.get_all_occupations()
            names = [occ.get("name", "") for occ in self._global_occupations if occ.get("name")]
            self.occ_combobox["values"] = names
            if names:
                self.occ_combobox.current(0)
        except Exception as e:
            print(f"Error cargando combo de ocupaciones: {e}")

    def _add_occupation_to_list(self):
        selected_name = self.occ_combo_var.get()
        if not selected_name:
            return

        found_occ = next((o for o in self._global_occupations if o.get("name") == selected_name), None)
        if not found_occ:
            return

        occ_id = found_occ.get("occupation_id") or found_occ.get("id")

        if any(o["id"] == occ_id for o in self._selected_occupations):
            messagebox.showwarning("Atención", "Esta ocupación ya fue agregada")
            return

        self._selected_occupations.append({"id": occ_id, "name": selected_name})
        self.occupations_listbox.insert("end", selected_name)

    def _remove_occupation_from_list(self):
        selected_index = self.occupations_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Atención", "Seleccione una ocupación de la lista para quitar")
            return
        
        idx = selected_index[0]
        self.occupations_listbox.delete(idx)
        if idx < len(self._selected_occupations):
            self._selected_occupations.pop(idx)

    # ---------------- Guardar y Otros ----------------
    
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

            ms_val = person.get("membership_status")
            if ms_val:
                self.combos["membership_status"].set(ms_val)

            self.combos["gender"].set(person.get("gender") or "")

            cons_obj = self.drop_helper.find_consolidation_by_id(person.get("consolidation_id"))
            if cons_obj: self.combos["consolidation_id"].set(cons_obj["level"])

            cdb_obj = self.drop_helper.find_cdb_by_id(person.get("cdb"))
            if cdb_obj: self.combos["cdb"].set(str(cdb_obj["number"]))

            self.combos["baptized"].set("Sí" if person.get("baptized") else "No")
            
            mems = self.controller.get_memberships(self.person_id) or []
            self.membership_editor.set_memberships(mems)

            # -------------------------------------------------------------
            # NUEVO: CARGAR LAS OCUPACIONES QUE YA TIENE LA PERSONA
            # -------------------------------------------------------------
            try:
                # Obtenemos las ocupaciones usando la función del controlador que ya creamos antes
                loaded_occups = self.controller.get_occupations(self.person_id) or []
                self._selected_occupations = []
                self.occupations_listbox.delete(0, tk.END)
                
                for occ in loaded_occups:
                    # Obtenemos de forma flexible la id y el nombre según devuelva tu JSON
                    o_id = occ.get("occupation_id") or occ.get("id")
                    o_name = occ.get("name")
                    if o_id and o_name:
                        self._selected_occupations.append({"id": o_id, "name": o_name})
                        self.occupations_listbox.insert("end", o_name)
            except Exception as ecc_err:
                print(f"Error cargando ocupaciones del usuario: {ecc_err}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_save(self):
        if not self.person_id: return
        
        payload = {}
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
        payload["membership_status"] = self.combos["membership_status"].get()

        # -------------------------------------------------------------
        # NUEVO: Enviamos la lista de ocupaciones en el payload (igual que el add)
        # -------------------------------------------------------------
        payload["occupation_ids"] = [occ["id"] for occ in self._selected_occupations]

        try:
            self.controller.update_person(self.person_id, payload)
            current_mems = self.membership_editor.memberships
            db_mems = [{"ministry_id": m["ministry_id"], "area_id": m["area_id"]} for m in current_mems]
            self.controller.update_memberships(self.person_id, db_mems)
            
            messagebox.showinfo("OK", "Actualizado correctamente")
            if self._on_data_changed: self._on_data_changed()

            self._clear_form()
            self.person_id = None
            
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
            elif isinstance(e, tk.Text):
                e.delete("1.0", tk.END)
            else:
                e.delete(0, tk.END) 

        for c in self.combos.values(): 
            c.set("") 

        self.membership_editor.clear()
        self._selected_occupations = []        # NUEVO: Limpia array temporal
        self.occupations_listbox.delete(0, tk.END) # NUEVO: Limpia caja visual
        self.person_id = None

    def refresh_dropdowns(self):
        # Compat: refresca todo
        self.drop_helper.refresh_all()
        self.drop_helper.fill_consolidations(self.combos["consolidation_id"])
        self.drop_helper.fill_cdbs(self.combos["cdb"])
        try:
            statuses = [s["name"] for s in self.config_service.get_marital_statuses()]
            self.combos["marital_status"]["values"] = statuses
        except Exception as e:
            print(f"Error al refrescar estados civiles: {e}")

        try:
            ms = [m["name"] for m in self.config_service.get_membership_statuses()]
            self.combos["membership_status"]["values"] = ms
        except Exception as e:
            print(f"Error al refrescar estados de membresía: {e}")

        self.membership_editor.refresh_ministry_combo() 
        self._refresh_occupations_combo() # NUEVO: Refresca el combobox en cambios globales

    # --- Métodos de refresh dirigidos para suscripción a eventos ---
    def refresh_cdb_combo(self, payload=None):
        try:
            self.drop_helper.refresh_cdb_cache()
            self.drop_helper.fill_cdbs(self.combos["cdb"])
        except Exception:
            pass

    def refresh_consolidations_combo(self, payload=None):
        try:
            self.drop_helper.refresh_consolidation_cache()
            self.drop_helper.fill_consolidations(self.combos["consolidation_id"])
        except Exception:
            pass

    def refresh_marital_combo(self, payload=None):
        try:
            self.drop_helper.refresh_marital_cache()
            try:
                statuses = [s["name"] for s in self.config_service.get_marital_statuses()]
                self.combos["marital_status"]["values"] = statuses
            except Exception:
                pass
        except Exception:
            pass

    def refresh_membership_combo(self, payload=None):
        try:
            self.drop_helper.refresh_membership_cache()
            try:
                ms = [m["name"] for m in self.config_service.get_membership_statuses()]
                self.combos["membership_status"]["values"] = ms
            except Exception:
                pass
        except Exception:
            pass

    def refresh_occupations(self, payload=None):
        try:
            self._refresh_occupations_combo()
        except Exception:
            pass

    def load_person_by_id(self, person_id: int):
        self._clear_form()
        self.entries["person_id"].insert(0, str(person_id))
        self._on_load()