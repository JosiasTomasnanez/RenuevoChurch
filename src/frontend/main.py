from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import threading
import time
import sys              
import urllib.request  
import json             
import os              
import subprocess      

from src.frontend.api.people_api import PeopleAPI
from src.frontend.api.config_api import ConfigAPI
from src.frontend.views.person_view import (
    AddPersonFrame,
    SearchPersonFrame,
    ModifyPersonFrame,
)
from src.frontend.views.config_view import ConfigurationFrame

CURRENT_VERSION = "1.0.0"

def _build_main_window():
    """Create and return a configured Tk main window instance."""

    class MainWindow(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Renuevo — Administración")
            self.withdraw()  
            
            self.people_api = PeopleAPI()
            self.config_api = ConfigAPI()
            
            self.dark_mode = False 
            self._show_splash()

        def _show_splash(self):
            self.splash = tk.Toplevel(self)
            
            if os.name == "nt": 
                self.splash.attributes("-toolwindow", True)
                self.splash.attributes("-topmost", True)
            self.splash.wm_attributes("-type", "splash") if os.name != "nt" else None
            
            self.splash.title("Iniciando Renuevo")
            self.splash.geometry("450x260")
            self.splash.config(bg="#F0E6F6")
            
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            self.splash.geometry(f"+{int(sw/2-225)}+{int(sh/2-130)}")
            
            mini_btn = tk.Button(
                self.splash, text="–", font=("Arial", 12, "bold"),
                bg="#F0E6F6", fg="#7A4A97", relief="flat", 
                activebackground="#E0D4E8", activeforeground="#7A4A97",
                command=self._minimize_splash, cursor="hand2"
            )
            mini_btn.place(x=420, y=5, width=25, height=25)
            
            tk.Label(self.splash, text="⛪ Iglesia Renuevo", font=("Arial", 16, "bold"), 
                     bg="#F0E6F6", fg="#7A4A97").pack(pady=(40, 5))
            
            self.status_lbl = tk.Label(self.splash, text="Iniciando...", 
                                       bg="#F0E6F6", fg="#5A5A5A", font=("Arial", 10))
            self.status_lbl.pack()

            self.pb = ttk.Progressbar(self.splash, mode="determinate", length=350, maximum=100)
            self.pb.pack(pady=20)

            threading.Thread(target=self._load_data_async, daemon=True).start()

        def _minimize_splash(self):
            self.deiconify()
            self.iconify()

        def _load_data_async(self):
            """Checklist de carga para asegurar que Render despertó y los datos están listos."""
            self.after(0, lambda: self.status_lbl.config(text="Conectando con el servidor..."))
            try:
                self.config_api.get_all_ministries()
            except Exception as e:
                print(f"Error al despertar el servidor: {e}")
            
            self.after(0, lambda: self.pb.config(value=25))
            time.sleep(0.2)

            self.after(0, lambda: self.status_lbl.config(text="Buscando actualizaciones..."))
            version_url = "https://renuevochurch.onrender.com/api/version" 
                
            try:
                with urllib.request.urlopen(version_url, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    latest_version = data.get("latest_version")
                    download_url = data.get("download_url")
                        
                    if latest_version and latest_version != CURRENT_VERSION:
                        self.after(0, lambda: self.status_lbl.config(
                            text=f"Nueva versión {latest_version} detectada. Descargando...", fg="#7A4A97"
                        ))
                            
                        if os.name == "nt":  
                            temp_dir = os.environ.get("TEMP", os.path.expanduser("~"))
                            installer_path = os.path.join(temp_dir, "RenuevoChurch_Setup_Update.exe")
                        else:  
                            temp_dir = "/tmp"
                            installer_path = os.path.join(temp_dir, "RenuevoChurch_Update.sh")
                            
                        urllib.request.urlretrieve(download_url, installer_path)
                        
                        if os.name != "nt":
                            os.chmod(installer_path, 0o755)
                            
                        self.after(0, lambda: self.status_lbl.config(text="Instalando y reiniciando...", fg="green"))
                        time.sleep(1)
                            
                        if os.name == "nt":
                            subprocess.Popen([installer_path, "/SILENT"])
                        else:
                            subprocess.Popen(["gnome-terminal", "--", installer_path]) 
                            
                        self.after(0, sys.exit)
                        return
            except Exception as version_err:
                print(f"No se pudo chequear actualizaciones (offline/timeout): {version_err}")
                
            self.after(0, lambda: self.pb.config(value=40))
            time.sleep(0.2)
            
            tasks = [
                ("Cargando niveles de consolidación...", self.config_api.get_all_consolidations, 70),
                ("Sincronizando base de datos de personas...", self.people_api.get_all_people, 90),
                ("Finalizando configuración...", None, 100)
            ]

            try:
                for i, (msg, func, progress_val) in enumerate(tasks):
                    self.after(0, lambda m=msg: self.status_lbl.config(text=m))
                    if func:
                        func() 
                    self.after(0, lambda v=progress_val: self.pb.config(value=v))
                    time.sleep(0.4)

                self.after(0, self._finish_initialization)
                
            except Exception as e:
                print(f"Error durante la carga: {e}")
                self.after(0, lambda: self.status_lbl.config(text="Error de conexión. Reintentando...", fg="red"))
                time.sleep(2)
                self.after(0, self._finish_initialization)

        def _finish_initialization(self):
            self.splash.destroy()
            self._build_ui()
            try:
                self.state("zoomed")
            except:
                self.attributes("-zoomed", True)
            self.deiconify()

        def _build_ui(self):
            self.style = ttk.Style()
            
            # --- BARRA SUPERIOR ---
            self.top_bar = tk.Frame(self)
            self.top_bar.pack(side="top", fill="x", pady=8)

            self.btn_config = tk.Button(
                self.top_bar, text="Configurar", command=lambda: self.show("config"),
                width=12, fg="darkblue"
            )
            self.btn_config.pack(side="left", padx=8)

            self.btn_frame = tk.Frame(self.top_bar)
            self.btn_frame.pack(side="left", expand=True, anchor="center")

            self.btn_add = tk.Button(self.btn_frame, text="Agregar", command=lambda: self.show("add"), width=12)
            self.btn_search = tk.Button(self.btn_frame, text="Busqueda", command=lambda: self.show("search"), width=12)
            self.btn_modify = tk.Button(self.btn_frame, text="Modificacion", command=lambda: self.show("modify"), width=12)

            self.btn_add.grid(row=0, column=0, padx=8)
            self.btn_search.grid(row=0, column=1, padx=8)
            self.btn_modify.grid(row=0, column=2, padx=8)

            self.btn_theme = tk.Button(
                self.top_bar, text="Tema: Claro ☀️", command=self._toggle_theme,
                width=14, bg="#2E3440", fg="white", activebackground="#1F232A",
                activeforeground="white", relief="flat", font=("Arial", 9, "bold")
            )
            self.btn_theme.pack(side="right", padx=12)

            # --- CONTENEDOR DE FRAMES ---
            self.main_container = tk.Frame(self)
            self.main_container.pack(fill="both", expand=True, padx=8, pady=8)

            self.frames = {}

            self.frames["search"] = SearchPersonFrame(self.main_container, self.people_api, self.config_api)
            self.frames["add"] = AddPersonFrame(
                self.main_container, self.people_api, self.config_api,
                on_data_changed=lambda: self.frames["search"]._on_search()
            )
            self.frames["modify"] = ModifyPersonFrame(
                self.main_container, self.people_api, self.config_api,
                on_data_changed=lambda: self.frames["search"]._on_search()
            )
            self.frames["config"] = ConfigurationFrame(self.main_container, self.config_api)

            config_f = self.frames["config"]
            for key in ["add", "modify", "search"]:
                if key in self.frames:
                    config_f._register_refresh_callback(self.frames[key].refresh_dropdowns)

            self.frames["search"]._open_modify_cb = self._open_modify

            for frame in self.frames.values():
                frame.place(relx=0, rely=0, relwidth=1, relheight=1)

            self.show("add")

        def _toggle_theme(self):
            """Alterna entre Claro y Oscuro protegiendo los botones y forzando la vista Configurar."""
            self.dark_mode = not self.dark_mode
            
            if self.dark_mode:
                # 🌙 PARÁMETROS DEL MODO OSCURO ELEGANTE
                bg_top = "#14161D"      
                bg_work = "#1E222B"     
                bg_card = "#282D37"     
                fg_text = "#E2E8F0"     
                
                self.btn_theme.config(text="Tema: Oscuro 🌙", bg=bg_card, fg=fg_text)
                
                # Fondo de ventanas principales
                self.config(bg=bg_top)
                self.top_bar.config(bg=bg_top)
                self.btn_frame.config(bg=bg_top)
                self.main_container.config(bg=bg_work)
                
                # Botonera Superior Principal
                for btn in [self.btn_add, self.btn_search, self.btn_modify]:
                    btn.config(bg=bg_card, fg=fg_text, activebackground="#343A46", activeforeground=fg_text)
                self.btn_config.config(bg=bg_card, fg="#93C5FD", activebackground="#343A46")

                # Ajustes globales para desplegables flotantes (Popdowns)
                self.option_add("*TCombobox*Listbox.background", bg_card)
                self.option_add("*TCombobox*Listbox.foreground", fg_text)
                self.option_add("*TCombobox*Listbox.selectBackground", "#7A4A97")
                self.option_add("*TCombobox*Listbox.selectForeground", "white")

                # Estilos del motor TTK 
                self.style.theme_use("default")
                self.style.configure(".", background=bg_work, foreground=fg_text)
                
                self.style.configure("Treeview", background=bg_work, fieldbackground=bg_work, foreground=fg_text)
                self.style.configure("Treeview.Heading", background=bg_card, foreground=fg_text, relief="flat")
                self.style.map("Treeview.Heading", background=[('active', '#343A46')])
                
                # 🛠️ CORRECCIÓN EXCLUSIVA PARA CONFIGURACIÓN (Estilos del Notebook extraídos del archivo 2)
                self.style.configure("TNotebook", background=bg_work, borderwidth=0, padding=0)
                self.style.configure("TNotebook.Tab", background=bg_card, foreground=fg_text, padding=[16, 6], lightcolor=bg_work, borderwidth=0)
                self.style.map("TNotebook.Tab", background=[("selected", "#7A4A97")], foreground=[("selected", "#FFFFFF")])

                self.style.configure("TLabel", background=bg_work, foreground=fg_text)
                self.style.configure("TFrame", background=bg_work)
                self.style.configure("TLabelframe", background=bg_work, foreground=fg_text)
                self.style.configure("TLabelframe.Label", background=bg_work, foreground=fg_text)
                self.style.configure("TCombobox", background=bg_card, fieldbackground=bg_card, foreground=fg_text, arrowcolor=fg_text)
                self.style.map("TCombobox", fieldbackground=[('readonly', bg_card)], foreground=[('readonly', fg_text)])

                # Recorremos todas las vistas aplicando el oscurecimiento profundo original
                for frame in self.frames.values():
                    self._apply_dark_recursively(frame, bg_work, bg_card, fg_text)
                    if hasattr(frame, "apply_theme"):
                        frame.apply_theme(dark_mode=True)
            else:
                # ☀️ RETORNO LIMPIO AL TEMA CLARO ORIGINAL
                self.btn_theme.config(text="Tema: Claro ☀️", bg="#2E3440", fg="white")
                
                self.config(bg="#F0F0F0")
                self.top_bar.config(bg="#F0F0F0")
                self.btn_frame.config(bg="#F0F0F0")
                self.main_container.config(bg="#F0F0F0")
                
                for btn in [self.btn_add, self.btn_search, self.btn_modify]:
                    btn.config(bg=SystemButtonFace, fg="black", activebackground="#EAEAEA", activeforeground="black")
                self.btn_config.config(bg=SystemButtonFace, fg="darkblue", activebackground="#EAEAEA")

                self.option_add("*TCombobox*Listbox.background", "white")
                self.option_add("*TCombobox*Listbox.foreground", "black")

                self.style.theme_use("vista" if os.name == "nt" else "clam")
                
                for frame in self.frames.values():
                    if hasattr(frame, "apply_theme"):
                        frame.apply_theme(dark_mode=False)
                    else:
                        self._apply_light_recursively(frame)

        def _apply_dark_recursively(self, widget, bg_work, bg_card, fg_text):
            """Pinta la app de forma exhaustiva incluyendo la sección Configurar sin tocar botones."""
            try:
                w_class = widget.winfo_class()
                
                # Forzar recuadros de fondo tradicionales y contenedores especiales de configuración
                if w_class in ("Frame", "LabelFrame", "TLabelframe", "TFrame"):
                    widget.config(bg=bg_work, highlightbackground=bg_work) if hasattr(widget, "config") else None
                elif w_class in ("Label", "TLabel"):
                    widget.config(bg=bg_work, fg=fg_text) if hasattr(widget, "config") else None
                elif w_class in ("Entry", "Text"):
                    widget.config(bg=bg_card, fg=fg_text, insertbackground=fg_text, relief="flat") if hasattr(widget, "config") else None
                elif w_class == "Listbox":
                    widget.config(bg=bg_card, fg=fg_text, selectbackground="#7A4A97", selectforeground="white", relief="flat") if hasattr(widget, "config") else None
                elif "combobox" in w_class.lower() or "date" in w_class.lower():
                    widget.config(background=bg_card, foreground=fg_text) if hasattr(widget, "config") else None
                
                # Los botones comunes ("Button") siguen completamente intactos para respetar tu diseño claro.

                for child in widget.winfo_children():
                    self._apply_dark_recursively(child, bg_work, bg_card, fg_text)
            except Exception:
                pass 

        def _apply_light_recursively(self, widget):
            """Devuelve de forma segura los contenedores al color base original sin alterar botones."""
            try:
                w_class = widget.winfo_class()
                if w_class in ("Frame", "LabelFrame", "TLabelframe", "TFrame"):
                    widget.config(bg="#F0F0F0") if hasattr(widget, "config") else None
                elif w_class in ("Label", "TLabel"):
                    widget.config(bg="#F0F0F0", fg="black") if hasattr(widget, "config") else None
                elif w_class in ("Entry", "Text"):
                    widget.config(bg="white", fg="black", insertbackground="black", relief="sunken") if hasattr(widget, "config") else None
                elif w_class == "Listbox":
                    widget.config(bg="white", fg="black", selectbackground="#0A246A", selectforeground="white", relief="sunken") if hasattr(widget, "config") else None
                elif "combobox" in w_class.lower() or "date" in w_class.lower():
                    widget.config(background="white", foreground="black") if hasattr(widget, "config") else None
                
                for child in widget.winfo_children():
                    self._apply_light_recursively(child)
            except Exception:
                pass

        def _open_modify(self, person_id: int, show: bool = True):
            mod = self.frames.get("modify")
            if not mod: return
            try:
                mod.load_person_by_id(person_id)
            except Exception as e:
                print(f"Error al cargar en modify: {e}")
            if show: self.show("modify")

        def show(self, key: str):
            for name, frame in self.frames.items():
                if name == key:
                    frame.lift()
                else:
                    frame.lower()

    SystemButtonFace = "SystemButtonFace" if os.name == "nt" else "#E1E1E1"
    return MainWindow()

def run_frontend():
    wnd = _build_main_window()
    wnd.mainloop()

if __name__ == "__main__":
    run_frontend()