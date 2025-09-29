// frontend/src/services/axios.js
import axios from "axios";

/**
 * Resuelve la base URL de la API de forma robusta:
 * 1) Si existe VITE_API_URL en build, úsala.
 * 2) Si NO existe, pero estamos en Pages (.pages.dev) o en el dominio del front,
 *    apunta directo al backend público.
 * 3) En dev local, cae a "/api".
 */
function resolveBaseURL() {
  let envBase;
  try {
    envBase = import.meta?.env?.VITE_API_URL;
  } catch (_) {
    envBase = undefined;
  }

  if (envBase) return String(envBase).replace(/\/$/, "");

  const host = typeof window !== "undefined" ? window.location.hostname : "";

  if (host.endsWith(".pages.dev") || host === "app.appquaculture.com") {
    return "https://api.appquaculture.com/api";
  }

  return "/api";
}

const BASE_URL = resolveBaseURL();

if (typeof window !== "undefined") {
  console.log("API BASE_URL =", BASE_URL);
  window.__API_BASE__ = BASE_URL;
}

const instance = axios.create({ baseURL: BASE_URL });
const refreshClient = axios.create({ baseURL: BASE_URL });

// Adjuntar token a cada solicitud si existe
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Manejar expiración y refrescar el token automáticamente
instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config || {};
    const status = error?.response?.status;
    const code = error?.response?.data?.code;

    // Intentar refresh cuando sea 401 (token vencido/no válido)
    if (status === 401 && !originalRequest._retry && (code === "token_not_valid" || true)) {
      originalRequest._retry = true;

      try {
        const storedUser = JSON.parse(localStorage.getItem("user") || "{}");
        const refreshToken = storedUser?.refresh || localStorage.getItem("refreshToken");
        if (!refreshToken) throw new Error("No refresh token");

        // ⚠️ IMPORTANTE: sin slash inicial para NO perder el /api del BASE_URL
        const { data } = await refreshClient.post("token/refresh/", { refresh: refreshToken });

        const newAccessToken = data?.access;
        if (!newAccessToken) throw new Error("No access token in refresh");

        // Guardar y actualizar headers por defecto
        localStorage.setItem("accessToken", newAccessToken);
        instance.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;

        // Asegurar header en el request original y reintentar
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        return instance(originalRequest);
      } catch (e) {
        // Si falla el refresh, limpiar y mandar a login
        localStorage.removeItem("accessToken");
        localStorage.removeItem("user");
        localStorage.removeItem("refreshToken");
        window.location.href = "/login";
        return Promise.reject(e);
      }
    }

    return Promise.reject(error);
  }
);

export default instance;
