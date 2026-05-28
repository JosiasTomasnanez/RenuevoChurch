import { ApiClient } from "./api_client";

const normalize = (res) => {
  if (res && typeof res === "object" && res.data) {
    return res.data;
  }
  return res || [];
};

export const ConfigAPI = {
  // =========================
  // MINISTRIES
  // =========================
  async getAllMinistries() {
    const res = await ApiClient.get("/config/ministries");
    return normalize(res);
  },

  createMinistry(data) {
    // Recibe { name: value } directo de los componentes
    return ApiClient.post("/config/ministries", data);
  },

  updateMinistry(ministry_id, name) {
    return ApiClient.put(`/config/ministries/${ministry_id}`, { name });
  },

  deleteMinistry(ministry_id) {
    return ApiClient.delete(`/config/ministries/${ministry_id}`);
  },

  // =========================
  // AREAS
  // =========================
  async getAreasByMinistry(ministry_id) {
    const res = await ApiClient.get(`/config/areas/by-ministry/${ministry_id}`);
    return normalize(res);
  },

  createArea(ministry_id, area) {
    return ApiClient.post("/config/areas", { ministry_id, area });
  },

  updateArea(area_id, area) {
    return ApiClient.put(`/config/areas/${area_id}`, { area });
  },

  deleteArea(area_id) {
    return ApiClient.delete(`/config/areas/${area_id}`);
  },

  // =========================
  // CONSOLIDATION
  // =========================
  async getAllConsolidations() {
    const res = await ApiClient.get("/config/consolidations");
    return normalize(res);
  },

  createConsolidation(data) {
    // Recibe { level: value }
    return ApiClient.post("/config/consolidations", data);
  },

  updateConsolidation(consolidation_id, level) {
    return ApiClient.put(`/config/consolidations/${consolidation_id}`, { level });
  },

  deleteConsolidation(consolidation_id) {
    return ApiClient.delete(`/config/consolidations/${consolidation_id}`);
  },

  // =========================
  // CDB
  // =========================
  async getAllCdbOptions() {
    const res = await ApiClient.get("/config/cdb");
    return normalize(res);
  },

  createCdb(data) {
    // Recibe { number: value }
    return ApiClient.post("/config/cdb", data);
  },

  updateCdb(cdb_id, number) {
    return ApiClient.put(`/config/cdb/${cdb_id}`, { number });
  },

  deleteCdb(cdb_id) {
    return ApiClient.delete(`/config/cdb/${cdb_id}`);
  },

  getCdbById(cdb_id) {
    return ApiClient.get(`/config/cdb/${cdb_id}`);
  },

  // =========================
  // MARITAL STATUS
  // =========================
  async getMaritalStatuses() {
    const res = await ApiClient.get("/config/marital-statuses");
    return normalize(res);
  },

  createMaritalStatus(data) {
    // Recibe { name: value }
    return ApiClient.post("/config/marital-statuses", data);
  },

  deleteMaritalStatus(status_id) {
    return ApiClient.delete(`/config/marital-statuses/${status_id}`);
  },

  // =========================
  // MEMBERSHIP STATUS
  // =========================
  async getMembershipStatuses() {
    const res = await ApiClient.get("/config/membership-statuses");
    return normalize(res);
  },

  createMembershipStatus(data) {
    // Recibe { name: value }
    return ApiClient.post("/config/membership-statuses", data);
  },

  deleteMembershipStatus(status_id) {
    return ApiClient.delete(`/config/membership-statuses/${status_id}`);
  },

  // =========================
  // OCCUPATIONS
  // =========================
  async getAllOccupations() {
    const res = await ApiClient.get("/config/occupations");
    return normalize(res);
  },

  getOccupationById(occupation_id) {
    return ApiClient.get(`/config/occupations/${occupation_id}`);
  },

  createOccupation(data) {
    // Recibe { name: value }
    return ApiClient.post("/config/occupations", data);
  },

  updateOccupation(occupation_id, name) {
    return ApiClient.put(`/config/occupations/${occupation_id}`, { name });
  },

  deleteOccupation(occupation_id) {
    return ApiClient.delete(`/config/occupations/${occupation_id}`);
  }
};