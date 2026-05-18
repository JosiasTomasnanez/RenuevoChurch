"""Helper for managing CRUD config tables.

Provides a generic widget factory and handlers for the repetitive CRUD pattern
used in ConfigurationFrame tabs (ministries, areas, consolidation, CDB).
"""
import tkinter as tk
from tkinter import messagebox
from typing import Callable, List, Dict, Optional


class ConfigTableHelper:
    """Generic helper for CRUD operations on config items in a listbox.
    
    Usage example in a config view:
        helper = ConfigTableHelper(
            label="Ministerio",
            entry_widget=self.ministry_name_entry,
            listbox_widget=self.ministry_listbox,
            on_get_items=self.config_service.get_all_ministries,
            on_add=self.config_service.add_ministry,
            on_update=self.config_service.update_ministry,
            on_delete=self.config_service.delete_ministry,
            display_key="name",  # which field to show in listbox
            item_id_key="ministry_id",  # unique ID key
        )
        
        helper.refresh_list()
        # Then bind button clicks to helper methods:
        # add_btn -> helper.add()
        # update_btn -> helper.update()
        # delete_btn -> helper.delete()
    """
    
    def __init__(
        self,
        label: str,
        entry_widget: tk.Widget,
        listbox_widget: tk.Listbox,
        on_get_items: Callable[[], List[Dict]],
        on_add: Callable[[str], int],
        on_update: Callable[[int, str], bool],
        on_delete: Callable[[int], bool],
        display_key: str = "name",
        item_id_key: str = "id",
        on_change: Optional[Callable[[], None]] = None,
    ):
        """Initialize the config table helper.
        
        Args:
            label: Display name for this config type ('Ministerio', 'Área', etc.)
            entry_widget: Input field (tk.Entry) for item data
            listbox_widget: tk.Listbox to display items
            on_get_items: Callable that returns all items
            on_add: Callable(value: str) -> id to add a new item
            on_update: Callable(id: int, value: str) -> bool to update an item
            on_delete: Callable(id: int) -> bool to delete an item
            display_key: Which field in the item dict to display in listbox
            item_id_key: Which field contains the unique item ID
            on_change: Optional callback called after successful add/update/delete
        """
        self.label = label
        self.entry_widget = entry_widget
        self.listbox_widget = listbox_widget
        self.on_get_items = on_get_items
        self.on_add = on_add
        self.on_update = on_update
        self.on_delete = on_delete
        self.display_key = display_key
        self.item_id_key = item_id_key
        self.on_change = on_change
        
        self._items = []
        self._selected_item_idx = None
        self._selected_item_id = None
        
        # Bind listbox selection
        self.listbox_widget.bind("<<ListboxSelect>>", self._on_listbox_select)
    
    def refresh_list(self):
        """Load all items and populate the listbox."""
        try:
            self._items = self.on_get_items() or []
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando {self.label.lower()}es: {e}")
            self._items = []
        
        self.listbox_widget.delete(0, tk.END)
        for item in self._items:
            display_value = item.get(self.display_key, "")
            self.listbox_widget.insert(tk.END, str(display_value))
        
        self._selected_item_idx = None
        self._selected_item_id = None
        self.entry_widget.delete(0, tk.END)
    
    def _on_listbox_select(self, event=None):
        """Handle listbox item selection."""
        sel = self.listbox_widget.curselection()
        if not sel:
            return
        
        idx = sel[0]
        self._selected_item_idx = idx
        
        if 0 <= idx < len(self._items):
            item = self._items[idx]
            self._selected_item_id = item.get(self.item_id_key)
            display_value = item.get(self.display_key, "")
            
            self.entry_widget.delete(0, tk.END)
            self.entry_widget.insert(0, str(display_value))
    
    # ... resto del código igual ...

    def add(self, **extra_args): # <--- CAMBIO: Agregamos **extra_args
        value = self.entry_widget.get().strip()
        if not value:
            messagebox.showerror("Error", f"Ingresá un {self.label.lower()}")
            return
        
        try:
            # CAMBIO: Pasamos extra_args a la función on_add
            self.on_add(value, **extra_args) 
            messagebox.showinfo("OK", f"{self.label} agregado")
            self.refresh_list()
            if self.on_change:
                self.on_change()
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar: {e}")

    def update(self, **extra_args): # <--- CAMBIO: Agregamos **extra_args
        if self._selected_item_id is None:
            messagebox.showerror("Error", f"Selecciona un {self.label.lower()}")
            return
        
        value = self.entry_widget.get().strip()
        if not value:
            messagebox.showerror("Error", f"Ingresá un {self.label.lower()}")
            return
        
        try:
            # CAMBIO: Pasamos el ID, el valor y los extras
            ok = self.on_update(self._selected_item_id, value, **extra_args)
            if ok:
                messagebox.showinfo("OK", f"{self.label} actualizado")
                self.refresh_list()
                if self.on_change:
                    self.on_change()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar {self.label.lower()}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {e}")
            
                
    def delete(self):
        """Delete the selected item."""
        if self._selected_item_id is None:
            messagebox.showerror("Error", f"Selecciona un {self.label.lower()}")
            return
        
        if not messagebox.askyesno("Confirmar", f"¿Eliminar este {self.label.lower()}?"):
            return
        
        try:
            ok = self.on_delete(self._selected_item_id)
            if ok:
                messagebox.showinfo("OK", f"{self.label} eliminado")
                self.refresh_list()
                if self.on_change:
                    self.on_change()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar {self.label.lower()}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {e}")
    
    @property
    def selected_item(self) -> Optional[Dict]:
        """Get the currently selected item dict."""
        if 0 <= (self._selected_item_idx or -1) < len(self._items):
            return self._items[self._selected_item_idx]
        return None
