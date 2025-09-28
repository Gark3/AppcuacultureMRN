// frontend/src/services/auth.js
import api from "./axios";

// Login contra SimpleJWT: POST /api/token/
export async function login(usuario, password) {
  try {
    const { data } = await api.post("/token/", {
      username: usuario,
      password: password,
    });
    // data = { access, refresh }

    // Guarda tokens
    localStorage.setItem("accessToken", data.access);
    localStorage.setItem("refreshToken", data.refresh);
    // Mantén compatibilidad si otras partes leen 'user.refresh'
    localStorage.setItem("user", JSON.stringify({ refresh: data.refresh }));

    // Fija el header Authorization para siguientes requests
    api.defaults.headers.common.Authorization = `Bearer ${data.access}`;

    // (Opcional) Si tienes un endpoint de perfil, complétalo:
    // const me = await api.get("/me/"); // ajusta si existe
    // return { ...data, ...me.data };

    return data;
  } catch (error) {
    const responseError = error.response?.data || { detail: "Error desconocido" };
    console.error("Error en login:", responseError);
    throw responseError;
  }
}
