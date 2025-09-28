// frontend/src/services/axios.js
import axios from "axios";

/**
 * Resuelve la base URL de la API de forma robusta:
 * 1) Si existe VITE_API_URL en build, úsala.
 * 2) Si NO existe, pero estamos en Pages (.pages.dev) o en producción del front,
 *    apunta directo al backend público.
 * 3) En dev local, cae a "/api".
 */
function resolveBaseURL() {
  let envBase;
  try {
    // Solo existe durante el build (Vite lo reemplaza)
    // En runtime de navegador puede tirar error, por eso el try/catch.
    envBase = import.meta?.env?.VITE_API_URL;
  } catch (_) {
    envBase = undefined;
  }

  if (envBase) return String(envBase).replace(/\/$/, "");

  const host =
    typeof window !== "undefined" ? window.location.hostname : "";

  // Si estamos en Preview/Pages o en el dominio del front, usa el backend público
  if (host.endsWith(".pages.dev") || host === "app.appquaculture.com") {
    return "https://api.appquaculture.com/api";
  }

  // Fallback para dev local con proxy
  return "/api";
}

const BASE_URL = resolveBaseURL();

// Exponer para inspección rápida en consola del navegador
if (typeof window !== "undefined") {
  console.log("API BASE_URL =", BASE_URL);
  window.__API_BASE__ = BASE_URL;
}

// Cliente principal de la app
const instance = axios.create({
  baseURL: BASE_URL, // ahora puedes llamar con rutas relativas: "/siembra/", "/usuario/..."
});

// Cliente sin interceptores para refrescar token (evita bucles)
const refreshClient = axios.create({
  baseURL: BASE_URL,
});

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

    // 401 por token inválido/expirado y aún no reintentada
    if (status === 401 && !originalRequest._retry && (code === "token_not_valid" || true)) {
      originalRequest._retry = true;

      try {
        const storedUser = JSON.parse(localStorage.getItem("user") || "{}");
        const refreshToken =
          storedUser?.refresh || localStorage.getItem("refreshToken");

        if (!refreshToken) throw new Error("No refresh token");

        // Usamos el cliente sin interceptores para evitar recursion
        const { data } = await refreshClient.post("/token/refresh/", {
          refresh: refreshToken,
        });

        const newAccessToken = data?.access;
        if (!newAccessToken) throw new Error("No access token in refresh");

        // Guarda y reintenta
        localStorage.setItem("accessToken", newAccessToken);
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        return instance(originalRequest);
      } catch (e) {
        // Si falla el refresh, limpia y manda a login
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
