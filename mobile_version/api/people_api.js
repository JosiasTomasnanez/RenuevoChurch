import { ApiClient } from "./api_client";

export const PeopleAPI = {
  BASE: "/people",

  getAllPeople() {
    return ApiClient.get("/people");
  },

  getPerson(personId) {
    return ApiClient.get(`/people/${personId}`);
  },

  getPersonMemberships(personId) {
    return ApiClient.get(`/people/${personId}/memberships`);
  },

  getPersonOccupations(personId) {
    return ApiClient.get(`/people/${personId}/occupations`);
  },

  getPeopleByMinistry(ministryId) {
    return ApiClient.get(`/people/by-ministry/${ministryId}`);
  },

  getPeopleByOccupation(occupationId) {
    return ApiClient.get(`/people/by-occupation/${occupationId}`);
  },

  searchPeople(query, partial = true) {
    return ApiClient.get("/people/search", { query, partial });
  },
  
  createPerson(data) {
    return ApiClient.post(`${PeopleAPI.BASE}/`, data);
  },

  updatePerson(personId, data) {
    return ApiClient.put(`${PeopleAPI.BASE}/${personId}`, data);
  },

  updatePersonMemberships(personId, memberships) {
    return ApiClient.put(`${PeopleAPI.BASE}/${personId}/memberships`, { memberships });
  },

  deletePerson(personId) {
    return ApiClient.delete(`${PeopleAPI.BASE}/${personId}`);
  }
};