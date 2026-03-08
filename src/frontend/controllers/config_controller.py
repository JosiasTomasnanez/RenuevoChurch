# src/frontend/controllers/config_controller.py
from typing import List, Dict, Optional

class ConfigController:
    """Controller layer for configuration-related GUI actions."""

    def __init__(self, config_service):
        self.service = config_service

    # ================================
    # Ministries
    # ================================
    def get_all_ministries(self) -> List[Dict]:
        return self.service.get_all_ministries()

    def create_ministry(self, name: str) -> None:
        self.service.create_ministry(name)

    def update_ministry(self, ministry_id: int, name: str) -> None:
        self.service.update_ministry(ministry_id, name)

    def delete_ministry(self, ministry_id: int) -> None:
        self.service.delete_ministry(ministry_id)

    # ================================
    # Areas
    # ================================
    def get_areas_by_ministry(self, ministry_id: int) -> List[Dict]:
        return self.service.get_areas_by_ministry(ministry_id)

    def create_area(self, ministry_id: int, area: str) -> None:
        self.service.create_area(ministry_id, area)

    def update_area(self, area_id: int, area: str) -> None:
        self.service.update_area(area_id, area)

    def delete_area(self, area_id: int) -> None:
        self.service.delete_area(area_id)

    # ================================
    # Consolidations
    # ================================
    def get_all_consolidations(self) -> List[Dict]:
        return self.service.get_all_consolidations()

    def create_consolidation(self, level: str) -> None:
        self.service.create_consolidation(level)

    def update_consolidation(self, consolidation_id: int, level: str) -> None:
        self.service.update_consolidation(consolidation_id, level)

    def delete_consolidation(self, consolidation_id: int) -> None:
        self.service.delete_consolidation(consolidation_id)

    # ================================
    # CDB
    # ================================
    def get_all_cdb_options(self) -> List[Dict]:
        return self.service.get_all_cdb_options()

    def get_cdb_by_id(self, cdb_id: int) -> Optional[Dict]:
        return self.service.get_cdb_by_id(cdb_id)

    def create_cdb(self, number: int) -> None:
        self.service.create_cdb(number)

    def update_cdb(self, cdb_id: int, number: int) -> None:
        self.service.update_cdb(cdb_id, number)

    def delete_cdb(self, cdb_id: int) -> None:
        self.service.delete_cdb(cdb_id)
