from .api_client import ApiClient


class ConfigAPI:

    @staticmethod
    def _normalize(res):
        if isinstance(res, dict):
            return res.get("data", [])
        return res

    # =========================
    # MINISTRIES
    # =========================

    @staticmethod
    def get_all_ministries():
        res = ApiClient.get("/config/ministries")
        return ConfigAPI._normalize(res)

    @staticmethod
    def create_ministry(name):
        return ApiClient.post("/config/ministries", {"name": name})

    @staticmethod
    def update_ministry(ministry_id, name):
        return ApiClient.put(f"/config/ministries/{ministry_id}", {"name": name})

    @staticmethod
    def delete_ministry(ministry_id):
        return ApiClient.delete(f"/config/ministries/{ministry_id}")

    # =========================
    # AREAS
    # =========================

    @staticmethod
    def get_areas_by_ministry(ministry_id):
        res = ApiClient.get(f"/config/areas/by-ministry/{ministry_id}")
        return ConfigAPI._normalize(res)

    @staticmethod
    def create_area(ministry_id, area):
        return ApiClient.post("/config/areas", {
            "ministry_id": ministry_id,
            "area": area
        })

    @staticmethod
    def update_area(area_id, area):
        return ApiClient.put(f"/config/areas/{area_id}", {
            "area": area
        })

    @staticmethod
    def delete_area(area_id):
        return ApiClient.delete(f"/config/areas/{area_id}")

    # =========================
    # CONSOLIDATION
    # =========================

    @staticmethod
    def get_all_consolidations():
        res = ApiClient.get("/config/consolidations")
        return ConfigAPI._normalize(res)

    @staticmethod
    def create_consolidation(level):
        return ApiClient.post("/config/consolidations", {
            "level": level
        })

    @staticmethod
    def update_consolidation(consolidation_id, level):
        return ApiClient.put(f"/config/consolidations/{consolidation_id}", {
            "level": level
        })

    @staticmethod
    def delete_consolidation(consolidation_id):
        return ApiClient.delete(f"/config/consolidations/{consolidation_id}")

    # =========================
    # CDB
    # =========================

    @staticmethod
    def get_all_cdb_options():
        res = ApiClient.get("/config/cdb")
        return ConfigAPI._normalize(res)

    @staticmethod
    def create_cdb(number):
        return ApiClient.post("/config/cdb", {"number": number})

    @staticmethod
    def update_cdb(cdb_id, number):
        return ApiClient.put(f"/config/cdb/{cdb_id}", {"number": number})

    @staticmethod
    def delete_cdb(cdb_id):
        return ApiClient.delete(f"/config/cdb/{cdb_id}")
    
    @staticmethod
    def get_cdb_by_id(cdb_id):
        return ApiClient.get(f"/config/cdb/{cdb_id}")
