<template>
  <div class="registro-usuario-container">
    <div class="registro-usuario-form">
      <h2>Crear Usuario</h2>

      <form @submit.prevent="registrarUsuario">
        <!-- Nombre -->
        <div class="form-group">
          <label for="nombre">Nombre:</label>
          <input type="text" id="nombre" v-model.trim="form.nombre" required />
          <small class="field-error" v-if="fieldErrors.first_name">{{ fieldErrors.first_name[0] }}</small>
        </div>

        <!-- Apellido -->
        <div class="form-group">
          <label for="apellido">Apellido:</label>
          <input type="text" id="apellido" v-model.trim="form.apellido" required />
          <small class="field-error" v-if="fieldErrors.last_name">{{ fieldErrors.last_name[0] }}</small>
        </div>

        <!-- Correo -->
        <div class="form-group">
          <label for="correo">Correo:</label>
          <input type="email" id="correo" v-model.trim="form.correo" required />
          <small class="field-error" v-if="fieldErrors.email">{{ fieldErrors.email[0] }}</small>
        </div>

        <!-- Usuario -->
        <div class="form-group">
          <label for="usuario">Usuario:</label>
          <input type="text" id="usuario" v-model.trim="form.usuario" required />
          <small class="field-error" v-if="fieldErrors.username">{{ fieldErrors.username[0] }}</small>
        </div>

        <!-- Contraseña -->
        <div class="form-group">
          <label for="password">Contraseña:</label>
          <input type="password" id="password" v-model="form.password" required />
          <small class="field-error" v-if="fieldErrors.password">{{ fieldErrors.password[0] }}</small>
        </div>

        <!-- Teléfono -->
        <div class="form-group">
          <label for="telefono">Teléfono:</label>
          <input type="text" id="telefono" v-model="form.telefono" @input="soloNumeros" required />
          <small class="field-error" v-if="fieldErrors.telefono">{{ fieldErrors.telefono[0] }}</small>
        </div>

        <!-- Sueldo -->
        <div class="form-group">
          <label for="sueldo">Sueldo:</label>
          <input type="number" step="0.01" id="sueldo" v-model.number="form.sueldo" required />
          <small class="field-error" v-if="fieldErrors.sueldo">{{ fieldErrors.sueldo[0] }}</small>
        </div>

        <!-- Acuícola (autocompletador) -->
        <div class="form-group">
          <label for="acuicola">Acuícola:</label>
          <input
            id="acuicola"
            v-model="acuicolaTexto"
            @input="onAcuicolaInput"
            list="lista-acuicolas"
            placeholder="Escribe y elige una acuícola"
            autocomplete="off"
            required
          />
          <datalist id="lista-acuicolas">
            <option
              v-for="a in acuicolasFiltradas"
              :key="a.id"
              :value="`${a.nombre} (ID: ${a.id})`"
            />
          </datalist>
          <small class="help">Selecciona una opción de la lista (queda guardado el ID).</small>
          <small class="field-error" v-if="fieldErrors.acuicola">{{ fieldErrors.acuicola[0] }}</small>
          <small class="pill" v-if="form.acuicola">Seleccionado: #{{ form.acuicola }}</small>
        </div>

        <!-- tipo_usuario fijo = 2 (no visible) -->

        <!-- Botón para registrar -->
        <button type="submit" :disabled="loading">
          {{ loading ? 'Registrando…' : 'Registrar' }}
        </button>
      </form>

      <p v-if="errorMsg" class="error-message">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script>
import axios from "@/services/publicAxios"; // baseURL debe apuntar a /api

export default {
  name: "RegistroUsuario",
  data() {
    return {
      // formulario visual
      form: {
        nombre: "",
        apellido: "",
        correo: "",
        usuario: "",
        password: "",
        telefono: "",
        sueldo: 0,
        acuicola: null,      // <- ID numérico que realmente envíamos
        tipo_usuario: 2      // <- fijo por defecto
      },
      // autocompletar acuícola
      acuicolaTexto: "",     // lo que escribe/ve el usuario
      acuicolas: [],         // todas las acuícolas del backend
      loading: false,
      errorMsg: "",
      fieldErrors: {}
    };
  },

  computed: {
    acuicolasFiltradas() {
      const q = this.acuicolaTexto.trim().toLowerCase();
      if (!q) return this.acuicolas;
      return this.acuicolas.filter(a =>
        [a.nombre, a.descripcion, String(a.id)]
          .filter(Boolean)
          .join(" ")
          .toLowerCase()
          .includes(q)
      );
    }
  },

  methods: {
    soloNumeros(e) {
      e.target.value = e.target.value.replace(/\D/g, "");
      this.form.telefono = e.target.value;
    },

    async cargarAcuicolas() {
      try {
        const { data } = await axios.get("/acuicola/");
        // Normaliza a {id, nombre, descripcion?}
        this.acuicolas = Array.isArray(data) ? data.map(x => ({
          id: x.id ?? x.id_acuicola ?? x.pk ?? null,
          nombre: x.nombre ?? x.name ?? "",
          descripcion: x.descripcion ?? ""
        })).filter(x => x.id) : [];
      } catch (e) {
        console.warn("No se pudieron cargar acuícolas:", e);
        this.acuicolas = [];
      }
    },

    onAcuicolaInput() {
      // Si el usuario elige una opción tipo: "Nombre (ID: 3)"
      const match = this.acuicolaTexto.match(/\(ID:\s*(\d+)\)/i);
      if (match) {
        this.form.acuicola = Number(match[1]);
      } else {
        // si escribe libre y no selecciona opción, reseteamos ID
        this.form.acuicola = null;
      }
    },

    validate() {
      this.fieldErrors = {};
      this.errorMsg = "";

      if (!this.form.nombre?.trim()) this.fieldErrors.first_name = ["Nombre requerido"];
      if (!this.form.apellido?.trim()) this.fieldErrors.last_name = ["Apellido requerido"];
      if (!this.form.usuario?.trim()) this.fieldErrors.username = ["Usuario requerido"];
      if (!this.form.password || this.form.password.length < 4)
        this.fieldErrors.password = ["Mínimo 4 caracteres"];
      if (!this.form.correo?.includes("@"))
        this.fieldErrors.email = ["Correo inválido"];

      const sueldoNum = Number(this.form.sueldo);
      if (Number.isNaN(sueldoNum)) this.fieldErrors.sueldo = ["Sueldo debe ser numérico"];

      if (!this.form.acuicola)
        this.fieldErrors.acuicola = ["Selecciona una acuícola de la lista"];

      return Object.keys(this.fieldErrors).length === 0;
    },

    buildPayload() {
      return {
        first_name: this.form.nombre.trim(),
        last_name: this.form.apellido.trim(),
        email: this.form.correo.trim(),
        username: this.form.usuario.trim(),
        password: this.form.password,
        telefono: this.form.telefono || "",
        sueldo: Number(this.form.sueldo || 0),
        acuicola: this.form.acuicola,  // <- ID
        tipo_usuario: 2                // <- fijo
      };
    },

    async registrarUsuario() {
      if (!this.validate()) return;

      this.loading = true;
      this.errorMsg = "";
      this.fieldErrors = {};

      try {
        const payload = this.buildPayload();
        await axios.post("/usuario/registrar/", payload);
        this.$router.push("/login");
      } catch (err) {
        const data = err?.response?.data;
        if (data && typeof data === "object") {
          if (data.detail) this.errorMsg = String(data.detail);
          Object.keys(data).forEach((k) => {
            if (k !== "detail") this.fieldErrors[k] = Array.isArray(data[k]) ? data[k] : [String(data[k])];
          });
          if (!this.errorMsg && !Object.keys(this.fieldErrors).length) {
            this.errorMsg = "Ocurrió un error al crear el usuario.";
          }
        } else {
          this.errorMsg = "Ocurrió un error al crear el usuario.";
        }
        console.error("Error al registrar usuario:", err);
      } finally {
        this.loading = false;
      }
    }
  },

  mounted() {
    this.cargarAcuicolas();
  }
};
</script>

<style scoped>
.registro-usuario-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.registro-usuario-form {
  background-color: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 12px;
  width: 360px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.registro-usuario-form h2 {
  text-align: center;
  margin-bottom: 18px;
}

.form-group {
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
}

label {
  font-weight: 600;
  margin-bottom: 6px;
}

input {
  padding: 10px 12px;
  border: 1px solid #d6d6d6;
  border-radius: 8px;
  outline: none;
}

input:focus {
  border-color: #8d2a2a;
  box-shadow: 0 0 0 3px rgba(141,42,42,0.1);
}

button {
  width: 100%;
  padding: 12px;
  border: none;
  background-color: #8d2a2a;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

button:hover { background-color: #5a3d31; }

.error-message {
  margin-top: 12px;
  color: #b00020;
  text-align: center;
}

.field-error {
  margin-top: 6px;
  color: #b00020;
  font-size: 0.85rem;
}

.help {
  margin-top: 6px;
  color: #666;
  font-size: 0.85rem;
}

.pill {
  display: inline-block;
  margin-top: 6px;
  background: #eef5ff;
  color: #2c5aa0;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.8rem;
}
</style>
