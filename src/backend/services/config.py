"""Configuration service - wrappers around config repository functions."""
from typing import Dict, List, Optional

from src.backend.db.repositories import config_repository as repo


class ConfigService:
    """Service layer for configuration-related operations."""
    
    # Ministry management
    def get_all_ministries(self) -> List[Dict]:
        """Get all ministries."""
        return repo.get_all_ministries()
    
    def get_ministry_by_id(self, ministry_id: int) -> Optional[Dict]:
        """Get a single ministry by id."""
        return repo.get_ministry_by_id(ministry_id)
    
    def create_ministry(self, name: str) -> int:
        """Create a new ministry."""
        return repo.create_ministry(name)
    
    def update_ministry(self, ministry_id: int, name: str) -> bool:
        """Update a ministry."""
        return repo.update_ministry(ministry_id, name)
    
    def delete_ministry(self, ministry_id: int) -> bool:
        """Delete a ministry."""
        return repo.delete_ministry(ministry_id)
    
    # Area management
    def get_all_areas(self) -> List[Dict]:
        """Get all ministry areas."""
        return repo.get_all_areas()
    
    def get_areas_by_ministry(self, ministry_id: int) -> List[Dict]:
        """Get areas for a specific ministry."""
        return repo.get_areas_by_ministry(ministry_id)
    
    def get_area_by_id(self, area_id: int) -> Optional[Dict]:
        """Get a single area by id."""
        return repo.get_area_by_id(area_id)
    
    def create_area(self, ministry_id: int, area: str) -> int:
        """Create a new ministry area."""
        return repo.create_area(ministry_id, area)
    
    def update_area(self, area_id: int, area: str) -> bool:
        """Update a ministry area."""
        return repo.update_area(area_id, area)
    
    def delete_area(self, area_id: int) -> bool:
        """Delete a ministry area."""
        return repo.delete_area(area_id)
    
    # Consolidation management
    def get_all_consolidations(self) -> List[Dict]:
        """Get all consolidation levels."""
        return repo.get_all_consolidations()
    
    def get_consolidation_by_id(self, consolidation_id: int) -> Optional[Dict]:
        """Get a single consolidation by id."""
        return repo.get_consolidation_by_id(consolidation_id)
    
    def create_consolidation(self, level: str) -> int:
        """Create a new consolidation level."""
        return repo.create_consolidation(level)
    
    def update_consolidation(self, consolidation_id: int, level: str) -> bool:
        """Update a consolidation level."""
        return repo.update_consolidation(consolidation_id, level)
    
    def delete_consolidation(self, consolidation_id: int) -> bool:
        """Delete a consolidation level."""
        return repo.delete_consolidation(consolidation_id)
    
    # CDB (Casa de Bendición) management
    def get_all_cdb_options(self) -> List[Dict]:
        """Get all CDB houses."""
        return repo.get_all_cdb_options()
    
    def get_cdb_by_id(self, cdb_id: int) -> Optional[Dict]:
        """Get a single CDB house by id."""
        return repo.get_cdb_by_id(cdb_id)
    
    def create_cdb(self, number: int) -> int:
        """Create a new CDB house."""
        return repo.create_cdb(number)
    
    def update_cdb(self, cdb_id: int, number: int) -> bool:
        """Update a CDB house."""
        return repo.update_cdb(cdb_id, number)
    
    def delete_cdb(self, cdb_id: int) -> bool:
        """Delete a CDB house."""
        return repo.delete_cdb(cdb_id)
    
    def get_marital_statuses(self) -> List[Dict]:
        """Get all marital status options."""
        return repo.get_marital_statuses()

    def create_marital_status(self, name: str) -> int:
        """Create a new marital status option."""
        return repo.create_marital_status(name)

    def delete_marital_status(self, status_id: int) -> bool:
        """Delete a marital status option."""
        return repo.delete_marital_status(status_id)
    
    def get_membership_statuses(self) -> List[Dict]:
        """Get all membership status options."""
        return repo.get_membership_statuses()

    def create_membership_status(self, name: str) -> int:
        """Create a new membership status option."""
        return repo.create_membership_status(name)

    def delete_membership_status(self, status_id: int) -> bool:
        """Delete a membership status option."""
        return repo.delete_membership_status(status_id)
    # Occupation management (Catálogo Maestro)
    def get_all_occupations(self) -> List[Dict]:
        """Get all master occupations."""
        return repo.get_all_occupations()

    def get_occupation_by_id(self, occupation_id: int) -> Optional[Dict]:
        """Get a single master occupation by id."""
        return repo.get_occupation_by_id(occupation_id)

    def create_occupation(self, name: str) -> int:
        """Create a new occupation option in the master catalog."""
        return repo.create_occupation(name)

    def update_occupation(self, occupation_id: int, name: str) -> bool:
        """Update an occupation name in the master table."""
        return repo.update_occupation(occupation_id, name)

    def delete_occupation(self, occupation_id: int) -> bool:
        """Delete an occupation option from the master table."""
        return repo.delete_occupation(occupation_id)

__all__ = ["ConfigService"]
