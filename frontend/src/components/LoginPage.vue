<template>
  <div class="login-container">
    <!-- Video de fondo -->
    <!--video autoplay muted @ended="mostrarLogin" class="video-fondo">
      <source src="@/assets/Diseño sin título.mp4" type="video/mp4" />
      Tu navegador no soporta el elemento de video.
    </video-->
    
    <!-- Formulario de login -->
    <div v-if="loginVisible" class="login-form">
      <h2>Iniciar sesión</h2>
      <form @submit.prevent="login">
        <label for="usuario">Usuario:</label>
        <!-- Se agrega id y name para cumplir con la accesibilidad -->
        <input
          type="text"
          id="usuario"
          name="usuario"
          v-model="usuario"
          required
        />
        <label for="password">Contraseña:</label>
        <!-- Se agrega id y name para cumplir con la accesibilidad -->
        <input
          type="password"
          id="password"
          name="password"
          v-model="password"
          required
        />
        <div class="buttons">
          <button type="submit">Iniciar sesión</button>
          <a href="#">¿Olvidaste tu contraseña?</a>
          <a href="#" @click.prevent="irRegistrarUsuario">Registrarse</a>
        </div>
        <p v-if="loginFailed" class="error-message">
          Usuario o contraseña incorrectos.
        </p>
      </form>
    </div>
  </div>
</template>

<script>
import { login as apiLogin } from '@/services/auth';

export default {
  name: "LoginPage",
  data() {
    return {
      loginVisible: true,
      usuario:'', // Valor de prueba, puedes quitarlo o modificarlo
      password: '', // Valor de prueba, puedes quitarlo o modificarlo
      loginFailed: false,
    };
  },
  methods: {
    mostrarLogin() {
      this.loginVisible = true;
    },
    async login() {
      try {
        // Se llama a la función de autenticación
        const response = await apiLogin(this.usuario, this.password);
        
        // Se espera un objeto JSON con: access, refresh, usuario_id, nombre, tipo_usuario, acuicola
        localStorage.setItem("accessToken", response.access);
        localStorage.setItem("user", JSON.stringify(response));

        this.$emit('login');   // Notifica al padre (por ejemplo, App.vue)
        this.loginFailed = false;
        // Redirecciona a la ruta principal
        this.$router.push('/');
      } catch (err) {
        this.loginFailed = true;
        console.error("Error de login:", err);
      }
    },
    irRegistrarUsuario() {
      // Redirige a la ruta de registro
      this.$router.push('/registrarusuario');
    }
  }
}
</script>

<style scoped>
.login-container {
  position: relative;
  width: 100%;
  height: 100vh;
}

.video-fondo {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -1;
}

.login-form {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(255, 255, 255, 0.9);
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.login-form h2 {
  text-align: center;
  margin-bottom: 20px;
}

.login-form form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.login-form label {
  font-weight: bold;
}

.login-form input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.login-form button {
  padding: 10px;
  border: none;
  background-color: #8d2a2a;
  color: white;
  border-radius: 5px;
  cursor: pointer;
}

.login-form button:hover {
  background-color: #5a3d31;
}

.login-form a {
  text-align: center;
  color: #8d2a2a;
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
}

.error-message {
  color: red;
  text-align: center;
}
</style>
