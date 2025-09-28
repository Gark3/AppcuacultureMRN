/// <reference types="vite/client" />
import axios from "axios";

// 👇 Usa la variable de entorno si existe; si no, cae a "/api"
axios.defaults.baseURL = import.meta.env.VITE_API_URL || "/api";