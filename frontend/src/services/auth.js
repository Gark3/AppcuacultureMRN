// frontend/src/services/auth.js
import api from "./axios";

/**
 * Autenticación usando tu endpoint personalizado:
 *   POST /api/login/
 * Body: { username, password }
 * Respuesta esperada:
 *   { refresh, access, usuario_id, nombre, tipo_usuario, acuicola }
 */
export async function login(usuario, password) {
  try {
    const { data } = await api.post("login/", {
      username: usuario,
      password: password,
    });

    // Validación mínima
    if (!data?.access) {
      throw new Error("Respuesta de login inválida: falta access token");
    }

    // Guarda TODO para que el resto de pantallas no dependan de llamadas extra
    localStorage.setItem("accessToken", data.access);
    localStorage.setItem("refreshToken", data.refresh || "");
    localStorage.setItem("user", JSON.stringify(data));
    // data.user ahora contiene, por ejemplo:
    // { access, refresh, usuario_id, nombre, tipo_usuario, acuicola }

    // Opcional: fija el header para la sesión actual
    api.defaults.headers.common.Authorization = `Bearer ${data.access}`;

    return data; // devuelve también los metadatos útiles
  } catch (error) {
    const responseError = error.response?.data || { detail: "Error desconocido" };
    console.error("Error en login:", responseError);
    throw responseError;
  }
}
