from src.frontend.api.api_client import ApiClient

class PeopleAPI:

    BASE = "/people"

    @staticmethod
    def create_person(data):
        return ApiClient.post(f"{PeopleAPI.BASE}/", data)

    @staticmethod
    def get_all_people():
        return ApiClient.get(f"{PeopleAPI.BASE}/")

    @staticmethod
    def get_person(person_id):
        return ApiClient.get(f"{PeopleAPI.BASE}/{person_id}")

    @staticmethod
    def search_people(query, partial=True):
        return ApiClient.get(
            f"{PeopleAPI.BASE}/search",
            params={"query": query, "partial": partial}
        )

    @staticmethod
    def update_person(person_id, data):
        return ApiClient.put(f"{PeopleAPI.BASE}/{person_id}", data)

    @staticmethod
    def delete_person(person_id):
        return ApiClient.delete(f"{PeopleAPI.BASE}/{person_id}")

    @staticmethod
    def get_memberships(person_id):
        return ApiClient.get(f"{PeopleAPI.BASE}/{person_id}/memberships")

    @staticmethod
    def get_people_by_ministry(ministry_id: int):
        return ApiClient.get(f"{PeopleAPI.BASE}/by-ministry/{ministry_id}")

    @staticmethod
    def update_memberships(person_id, memberships):
        return ApiClient.put(
            f"{PeopleAPI.BASE}/{person_id}/memberships",
            memberships
        )
    @staticmethod
    def get_people_by_occupation(occupation_id: int):
        """Obtiene las personas asociadas a una ocupación específica."""
        return ApiClient.get(f"{PeopleAPI.BASE}/by-occupation/{occupation_id}")

    @staticmethod
    def get_occupations(person_id):
        """Obtiene las ocupaciones de una persona específica."""
        return ApiClient.get(f"{PeopleAPI.BASE}/{person_id}/occupations")