import api from './axios';

const API_URL = 'login/';

export async function login(usuario, password) {
  try {
    const response = await api.post(API_URL, {
      username: usuario,
      password: password
    });

    const data = response.data;

    // ✅ Asegúrate de guardar TODA la respuesta, incluyendo usuario_id y acuicola
    console.log("🔍 Datos guardados del usuario:", data);
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('user', JSON.stringify(data));  // 🔥 Aquí está la clave

    return data;
  } catch (error) {
    const responseError = error.response?.data || { detail: 'Error desconocido' };
    console.error("Error en login:", responseError);
    throw responseError;
  }
}
