from src.frontend.views._base import BaseFrame, tk, messagebox, ttk
from src.frontend.helpers.config_dropdown_helper import ConfigDropdownHelper
from src.frontend.helpers.membership_editor_helper import MembershipEditorHelper 
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
        self._selected_occupations = []
        
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

        # --- LADO IZQUIERDO ---
        fields = [
            ("first_name", "Nombre *"),
            ("last_name", "Apellido *"),
            ("email", "Correo"),
            ("birthdate", "Fecha de nacimiento"),
            ("gender", "Género"),
            ("dni", "DNI"),
            ("phone_number", "Teléfono"),
            ("marital_status", "Estado civil"),
            ("membership_status", "Estado de membresía"),
            ("social_security", "Seguro Social"),
            ("street", "Calle"),
            ("neighborhood", "Barrio"),
            ("house_number", "Número de casa"),
            ("consolidation_id", "Nivel de consolidación"),
            ("cdb", "¿CDB?"),
            ("baptized", "¿Bautizado?"),
        ]

        for i, (key, label) in enumerate(fields):
            tk.Label(
                left,
                text=label,
                bg=self.BG_PRIMARY,
                fg=self.TEXT_DARK
            ).grid(row=i, column=0, sticky="w", padx=6, pady=3)

            if key in ["consolidation_id", "cdb", "baptized", "gender", "marital_status", "membership_status"]:
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
                    date_pattern='yyyy-mm-dd',
                    locale='es_ES',
                    headersbackground='#E6D5F2'
                )

                cal.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = cal

            else:
                ent = tk.Entry(
                    left,
                    width=40,
                    bg=self.BG_INPUT,
                    fg=self.TEXT_DARK,
                    relief="solid",
                    bd=1
                )

                ent.grid(row=i, column=1, sticky="w", padx=6, pady=3)
                self.entries[key] = ent

        self.drop_helper.fill_consolidations(self.combos["consolidation_id"])
        self.drop_helper.fill_cdbs(self.combos["cdb"])
        self.drop_helper.fill_marital_statuses(self.combos["marital_status"])
        self.drop_helper.fill_membership_statuses(self.combos["membership_status"])

        self.combos["gender"]["values"] = ["Masculino", "Femenino"]

        self.combos["baptized"]["values"] = ["Sí", "No"]
        self.combos["baptized"].set("No")

        tk.Button(
            left,
            text="Agregar persona",
            command=self._on_submit,
            bg=self.BTN_COLOR,
            fg="white"
        ).grid(row=len(fields), column=0, columnspan=2, pady=(12, 0))

        # --- LADO DERECHO ---
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

        # --- FRAME INDEPENDIENTE PARA CONTACTO ---
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

        occupations_frame = tk.Frame(right, bg=self.BG_PRIMARY)
        occupations_frame.grid(row=2, column=0, sticky="w", pady=(15, 0))

        tk.Label(
            occupations_frame,
            text="Ocupaciones / Oficios",
            bg=self.BG_PRIMARY,
            fg=self.TEXT_DARK,
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="w", pady=(0, 3))

        # Fila para el combo y el botón agregar
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

        # Listbox visual de lo que se va cargando
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

        # Botón Quitar abajo de la lista
        tk.Button(
            occupations_frame,
            text="Quitar seleccionado",
            command=self._remove_occupation_from_list,
            bg="#c0392b",
            fg="white",
            padx=5
        ).pack(anchor="w")
        
        # Poblamos el combobox por primera vez
        self._refresh_occupations_combo()



    def _refresh_occupations_combo(self):
        """Busca todas las ocupaciones globales y llena el Combobox desplegable."""
        try:
            self._global_occupations = self.config_service.get_all_occupations()
            names = [occ.get("name", "") for occ in self._global_occupations if occ.get("name")]
            self.occ_combobox["values"] = names
            if names:
                self.occ_combobox.current(0)
        except Exception as e:
            print(f"Error cargando combo de ocupaciones: {e}")

    def _add_occupation_to_list(self):
        """Agrega la ocupación seleccionada en el combo a la lista temporal."""
        selected_name = self.occ_combo_var.get()
        if not selected_name:
            return

        # Encontrar el objeto completo para tener el ID
        found_occ = next((o for o in self._global_occupations if o.get("name") == selected_name), None)
        if not found_occ:
            return

        occ_id = found_occ.get("occupation_id") or found_occ.get("id")

        # Evitar duplicados en la lista interna
        if any(o["id"] == occ_id for o in self._selected_occupations):
            messagebox.showwarning("Atención", "Esta ocupación ya fue agregada")
            return

        # Guardar en memoria temporal y mostrar en la lista visual
        self._selected_occupations.append({"id": occ_id, "name": selected_name})
        self.occupations_listbox.insert("end", selected_name)

    def _remove_occupation_from_list(self):
        """Quita el elemento seleccionado en el Listbox de la lista temporal."""
        selected_index = self.occupations_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Atención", "Seleccione una ocupación de la lista para quitar")
            return
        
        idx = selected_index[0]
        # Borrar de la lista visual y de nuestro arreglo en memoria
        self.occupations_listbox.delete(idx)
        if idx < len(self._selected_occupations):
            self._selected_occupations.pop(idx)


    def _on_submit(self):
        payload = {}
        
        for k, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                val = widget.get("1.0", "end-1c").strip()
            else:
                val = widget.get() or None
            payload[k] = val if val != "" else None
        
        if not payload.get("first_name") or not payload.get("last_name"):
            messagebox.showerror("Error", "Nombre y Apellido son obligatorios")
            return

        payload["gender"] = self.combos["gender"].get() 
        payload["baptized"] = self.combos["baptized"].get() == "Sí"
        payload["marital_status"] = self.combos["marital_status"].get()
        payload["membership_status"] = self.combos["membership_status"].get()
        payload["consolidation_id"] = self.drop_helper.get_consolidation_id(self.combos["consolidation_id"].get())
        payload["cdb"] = self.drop_helper.get_cdb_id(self.combos["cdb"].get())

        try:
            person_id = self.controller.create_person(payload)
            current_mems = self.membership_editor.memberships
            if current_mems:
                db_mems = [{"ministry_id": m["ministry_id"], "area_id": m["area_id"]} for m in current_mems]
                self.controller.update_memberships(person_id, db_mems)

            selected_occ_ids = [occ["id"] for occ in self._selected_occupations]
            
            if hasattr(self.controller, "update_person_occupations"):
                self.controller.update_person_occupations(person_id, selected_occ_ids)

            messagebox.showinfo("OK", "Persona creada exitosamente")
            self._clear_form()
            if self._on_data_changed:
                self._on_data_changed()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _clear_form(self):
        for e in self.entries.values(): 
            if isinstance(e, tk.Text):
                e.delete("1.0", "end")
            else:
                e.delete(0, "end")
                
        for c in self.combos.values(): c.set("")
        self.combos["baptized"].set("No")
        self.combos["gender"].set("Masculino")
        self.membership_editor.clear() 
        self._selected_occupations = []
        self.occupations_listbox.delete(0, "end")

    def refresh_dropdowns(self):
        """Llamado cuando cambia la configuración global"""
        self.drop_helper.refresh_all()
        self.drop_helper.fill_consolidations(self.combos["consolidation_id"])
        self.drop_helper.fill_cdbs(self.combos["cdb"])
        self.drop_helper.fill_marital_statuses(self.combos["marital_status"])
        self.drop_helper.fill_membership_statuses(self.combos["membership_status"])
        self.membership_editor.refresh_ministry_combo()
        self._refresh_occupations_combo()