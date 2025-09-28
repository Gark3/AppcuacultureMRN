import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:8000//api/',
});

// Adjuntar token a cada solicitud si existe
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');  // Corrige: debe ser 'accessToken'
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Manejar expiración y refrescar el token automáticamente
instance.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // Verifica si es un error 401 por token expirado y no se ha reintentado
    if (
      error.response &&
      error.response.status === 401 &&
      error.response.data.code === 'token_not_valid' &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        // Obtener refresh token desde el localStorage
        const storedUser = localStorage.getItem('user');
        const refreshToken = storedUser ? JSON.parse(storedUser).refresh : null;

        if (!refreshToken) throw new Error("No refresh token");

        // Hacer solicitud para refrescar token
        const res = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refreshToken
        });

        const newAccessToken = res.data.access;

        // Guardar el nuevo token y actualizar cabecera
        localStorage.setItem('accessToken', newAccessToken);
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        return instance(originalRequest); // Reintenta la petición original
      } catch (refreshError) {
        // Si falla el refresh, limpiar localStorage y redirigir a login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default instance;
