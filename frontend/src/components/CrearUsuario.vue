<template>
  <div class="registro-usuario-container">
    <div class="registro-usuario-form">
      <h2>Crear Usuario</h2>
      <form @submit.prevent="registrarUsuario">
        <!-- Nombre -->
        <div class="form-group">
          <label for="nombre">Nombre:</label>
          <input type="text" id="nombre" v-model="form.nombre" required />
        </div>

        <!-- Apellido -->
        <div class="form-group">
          <label for="apellido">Apellido:</label>
          <input type="text" id="apellido" v-model="form.apellido" required />
        </div>

        <!-- Correo -->
        <div class="form-group">
          <label for="correo">Correo:</label>
          <input type="email" id="correo" v-model="form.correo" required />
        </div>

        <!-- Usuario -->
        <div class="form-group">
          <label for="usuario">Usuario:</label>
          <input type="text" id="usuario" v-model="form.usuario" required />
        </div>

        <!-- Contraseña -->
        <div class="form-group">
          <label for="password">Contraseña:</label>
          <input type="password" id="password" v-model="form.password" required />
        </div>

        <!-- Teléfono -->
        <div class="form-group">
          <label for="telefono">Teléfono:</label>
          <input type="text" id="telefono" v-model="form.telefono" @input="soloNumeros" required />
        </div>

        <!-- Sueldo -->
        <div class="form-group">
          <label for="sueldo">Sueldo:</label>
          <input type="number" step="0.01" id="sueldo" v-model.number="form.sueldo" required />
        </div>

        <!-- Botón para registrar -->
        <button type="submit">Registrar</button>
      </form>
      <p v-if="errorMsg" class="error-message">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script>
import axios from '@/services/publicAxios';

export default {
  name: "RegistroUsuario",
  data() {
    return {
      form: {
        nombre: "",
        apellido: "",
        correo: "",
        usuario: "",
        password: "",
        telefono: "",
        sueldo: 0
      },
      errorMsg: ""
    };
  },
  methods: {
    soloNumeros(e) {
      e.target.value = e.target.value.replace(/\D/g, '');
      this.form.telefono = e.target.value;
    },
    async registrarUsuario() {
      try {
        const payload = {
          first_name: this.form.nombre,
          last_name: this.form.apellido, 
          email: this.form.correo,
          username: this.form.usuario,
          password: this.form.password,
          telefono: this.form.telefono,
          sueldo: this.form.sueldo,
          acuicola: 1,
          tipo_usuario: 1
        };

        await axios.post("http://localhost:8000/api/usuario/registrar/", payload);
        this.$router.push("/login");
      } catch (error) {
        console.error("Error al registrar usuario:", error);
        this.errorMsg = "Ocurrió un error al crear el usuario.";
      }
    }
  }
};
</script>

<style scoped>
.registro-usuario-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f8f9fa;
}

.registro-usuario-form {
  background-color: rgba(255, 255, 255, 0.9);
  padding: 30px;
  border-radius: 10px;
  width: 350px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.registro-usuario-form h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

label {
  font-weight: bold;
  margin-bottom: 5px;
}

input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  width: 100%;
  padding: 12px;
  border: none;
  background-color: #8d2a2a;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

button:hover {
  background-color: #5a3d31;
}

.error-message {
  margin-top: 10px;
  color: red;
  text-align: center;
}
</style>
