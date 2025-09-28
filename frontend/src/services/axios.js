// frontend/src/services/axios.js
import axios from "axios";

// Usa variable de entorno en build (Cloudflare Pages) o cae a "/api"
const BASE_URL = (import.meta?.env?.VITE_API_URL ?? "/api").replace(/\/$/, "");

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
        // refresh guardado en localStorage (ajusta si usas otra clave)
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
        // Ajusta la ruta si tu login está en otro path
        window.location.href = "/login";
        return Promise.reject(e);
      }
    }

    return Promise.reject(error);
  }
);

export default instance;
