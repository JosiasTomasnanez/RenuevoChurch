"""Lightweight event bus for frontend config changes.

Allows components to subscribe to named events (like 'cdb.updated') and
publishes only the relevant updates so views can refresh minimally.
"""
from typing import Callable, Dict, List


class ConfigManager:
    _instance = None

    def __init__(self):
        self._subs: Dict[str, List[Callable]] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance

    def subscribe(self, event_name: str, callback: Callable):
        lst = self._subs.setdefault(event_name, [])
        if callback not in lst:
            lst.append(callback)

    def unsubscribe(self, event_name: str, callback: Callable):
        if event_name in self._subs and callback in self._subs[event_name]:
            self._subs[event_name].remove(callback)

    def publish(self, event_name: str, payload=None):
        for cb in list(self._subs.get(event_name, [])):
            try:
                cb(payload) if payload is not None else cb()
            except Exception:
                pass


__all__ = ["ConfigManager"]
