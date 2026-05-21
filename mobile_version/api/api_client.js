
const BASE_URL = "https://renuevochurch.onrender.com";

export const ApiClient = {
  async request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    
    options.headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        // 🔍 LEEMOS EL DETALLE DEL ERROR QUE ENVÍA TU BACKEND (FastAPI/Flask)
        const errorDetail = await response.text();
        console.error(`❌ El servidor rechazó la petición con código ${response.status}. Detalle:`, errorDetail);
        throw new Error(`HTTP error! status: ${response.status} - ${errorDetail}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`🚨 Error de red o código en la petición API (${endpoint}):`, error.message);
      throw error;
    }
  },

  get(endpoint, params = null) {
    // Aseguramos que empiece con barra si no la tiene
    let cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    
    if (params) {
      const query = new URLSearchParams(params).toString();
      cleanEndpoint = `${cleanEndpoint}?${query}`;
    }
    
    return ApiClient.request(cleanEndpoint, { method: "GET" });
  },

  post(endpoint, data = null) {
    return ApiClient.request(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : null,
    });
  },

  put(endpoint, data = null) {
    return ApiClient.request(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : null,
    });
  },

  delete(endpoint) {
    return ApiClient.request(endpoint, { method: "DELETE" });
  }
};