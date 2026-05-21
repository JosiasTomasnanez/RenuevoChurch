import { ApiClient } from "./api_client";

export const PeopleAPI = {
  BASE: "/people",

  getAllPeople() {
    return ApiClient.get("/people");
  },

  getPerson(personId) {
    return ApiClient.get(`/people/${personId}`);
  },

  searchPeople(query, partial = true) {
    return ApiClient.get("/people/search", { query, partial });
  },
  
  createPerson(data) {
    return ApiClient.post(`${PeopleAPI.BASE}/`, data);
  },

  deletePerson(personId) {
    return ApiClient.delete(`${PeopleAPI.BASE}/${personId}`);
  }
};