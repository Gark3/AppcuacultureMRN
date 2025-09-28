// src/lib/http.ts
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  withCredentials: false, // pon true solo si usas cookies/sesión
});
