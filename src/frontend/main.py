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
            
            self._show_splash()

        def _show_splash(self):
            self.splash = tk.Toplevel(self)
            self.splash.overrideredirect(True)
            self.splash.geometry("450x250")
            self.splash.config(bg="#F0E6F6")
            
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            self.splash.geometry(f"+{int(sw/2-225)}+{int(sh/2-125)}")
            
            tk.Label(self.splash, text="⛪ Iglesia Renuevo", font=("Arial", 16, "bold"), 
                     bg="#F0E6F6", fg="#7A4A97").pack(pady=(30, 10))
            
            self.status_lbl = tk.Label(self.splash, text="Iniciando...", 
                                       bg="#F0E6F6", fg="#5A5A5A", font=("Arial", 10))
            self.status_lbl.pack()

            self.pb = ttk.Progressbar(self.splash, mode="determinate", length=350, maximum=100)
            self.pb.pack(pady=20)

            threading.Thread(target=self._load_data_async, daemon=True).start()

        def _load_data_async(self):
            """Checklist de carga para asegurar que Render despertó y los datos están listos."""
            

            self.after(0, lambda: self.status_lbl.config(text="Buscando actualizaciones..."))
                
            version_url = "https://tu-app.onrender.com/api/version" 
                
            try:
                with urllib.request.urlopen(version_url, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    latest_version = data.get("latest_version")
                    download_url = data.get("download_url")
                        
                    if latest_version and latest_version != CURRENT_VERSION:
                        self.after(0, lambda: self.status_lbl.config(
                            text=f"Nueva versión {latest_version} detectada. Descargando...", fg="#7A4A97"
                        ))
                            
                        temp_dir = os.environ.get("TEMP", os.path.expanduser("~"))
                        installer_path = os.path.join(temp_dir, "RenuevoChurch_Setup_Update.exe")
                            
                        urllib.request.urlretrieve(download_url, installer_path)
                            
                        self.after(0, lambda: self.status_lbl.config(text="Instalando y reiniciando...", fg="green"))
                        time.sleep(1)
                            
                        subprocess.Popen([installer_path, "/SILENT"]) 
                            
                        self.after(0, sys.exit)
                        return
            except Exception as version_err:
                print(f"No se pudo chequear actualizaciones (offline/timeout): {version_err}")
                
            # Actualizamos barra inicial tras superar o skippear el chequeo
            self.after(0, lambda: self.pb.config(value=10))
            time.sleep(0.2)
            
            
            
            tasks = [
                ("Conectando con el servidor...", self.config_api.get_all_ministries, 30),
                ("Cargando niveles de consolidación...", self.config_api.get_all_consolidations, 60),
                ("Sincronizando base de datos de personas...", self.people_api.get_all_people, 90),
                ("Finalizando configuración...", None, 100)
            ]

            try:
                for i, (msg, func, progress_val) in enumerate(tasks):
                    # Actualizar texto en UI
                    self.after(0, lambda m=msg: self.status_lbl.config(text=m))
                    
                    # Ejecutar petición real
                    if func:
                        func() 
                    
                    # Actualizar barra
                    self.after(0, lambda v=progress_val: self.pb.config(value=v))
                    
                    # Pequeña pausa visual para que no sea un parpadeo
                    time.sleep(0.4)

                # Todo listo, abrir App
                self.after(0, self._finish_initialization)
                
            except Exception as e:
                print(f"Error durante la carga: {e}")
                # Si falla algo, intentamos abrir igual después de un aviso
                self.after(0, lambda: self.status_lbl.config(text="Error de conexión. Reintentando...", fg="red"))
                time.sleep(2)
                self.after(0, self._finish_initialization)

        def _finish_initialization(self):
            self.splash.destroy()
            
            # Construimos la UI real
            self._build_ui()
            
            # Maximizar y mostrar
            try:
                self.state("zoomed")
            except:
                self.attributes("-zoomed", True)
            self.deiconify()

        def _build_ui(self):
            # --- BARRA SUPERIOR ---
            top = tk.Frame(self)
            top.pack(side="top", fill="x", pady=8)

            self.btn_config = tk.Button(
                top, text="Configurar", command=lambda: self.show("config"),
                width=12, fg="darkblue"
            )
            self.btn_config.pack(side="left", padx=8)

            btn_frame = tk.Frame(top)
            btn_frame.pack(anchor="n", expand=True)

            self.btn_add = tk.Button(btn_frame, text="Agregar", command=lambda: self.show("add"), width=12)
            self.btn_search = tk.Button(btn_frame, text="Busqueda", command=lambda: self.show("search"), width=12)
            self.btn_modify = tk.Button(btn_frame, text="Modificacion", command=lambda: self.show("modify"), width=12)

            self.btn_add.grid(row=0, column=0, padx=8)
            self.btn_search.grid(row=0, column=1, padx=8)
            self.btn_modify.grid(row=0, column=2, padx=8)

            # --- CONTENEDOR DE FRAMES ---
            container = tk.Frame(self)
            container.pack(fill="both", expand=True, padx=8, pady=8)

            self.frames = {}

            # Instanciación de Frames (ahora los datos ya estarán en cache/memoria)
            self.frames["search"] = SearchPersonFrame(container, self.people_api, self.config_api)
            self.frames["add"] = AddPersonFrame(
                container, self.people_api, self.config_api,
                on_data_changed=lambda: self.frames["search"]._on_search()
            )
            self.frames["modify"] = ModifyPersonFrame(
                container, self.people_api, self.config_api,
                on_data_changed=lambda: self.frames["search"]._on_search()
            )
            self.frames["config"] = ConfigurationFrame(container, self.config_api)

            # Callbacks de refresco
            config_f = self.frames["config"]
            for key in ["add", "modify", "search"]:
                if key in self.frames:
                    config_f._register_refresh_callback(self.frames[key].refresh_dropdowns)

            # Enlace Search -> Modify
            self.frames["search"]._open_modify_cb = self._open_modify

            # Posicionar frames
            for frame in self.frames.values():
                frame.place(relx=0, rely=0, relwidth=1, relheight=1)

            self.show("add")

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

    return MainWindow()

def run_frontend():
    wnd = _build_main_window()
    wnd.mainloop()

if __name__ == "__main__":
    run_frontend()