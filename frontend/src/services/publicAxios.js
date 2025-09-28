// frontend/src/services/publicAxios.js
import axios from "axios";

const BASE_URL = (import.meta?.env?.VITE_API_URL ?? "/api").replace(/\/$/, "");

const publicAxios = axios.create({
  baseURL: BASE_URL, // igual que el privado, pero SIN header Authorization
});

export default publicAxios;
