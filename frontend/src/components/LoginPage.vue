<template>
  <div class="login-container">
    <!-- Video de fondo -->
    <!--
    <video autoplay muted @ended="mostrarLogin" class="video-fondo">
      <source src="@/assets/Diseño sin título.mp4" type="video/mp4" />
      Tu navegador no soporta el elemento de video.
    </video>
    -->

    <!-- Wrapper con logos laterales y formulario -->
    <div v-if="loginVisible" class="login-wrapper">
      <!-- Logo IPN (izquierda) -->
      <img
        class="side-logo side-logo-left"
        src="@/assets/ipnlogo.png"
        alt="Logo del IPN"
        draggable="false"
      />

      <!-- Formulario de login -->
      <div class="login-form">
        <h2>Iniciar sesión</h2>
        <form @submit.prevent="login">
          <label for="usuario">Usuario:</label>
          <input
            type="text"
            id="usuario"
            name="usuario"
            v-model="usuario"
            required
          />

          <label for="password">Contraseña:</label>
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

      <!-- Logo CIIDIR (derecha) -->
      <img
        class="side-logo side-logo-right"
        src="@/assets/ciidirlogo.png"
        alt="Logo de CIIDIR"
        draggable="false"
      />
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
      usuario: '',
      password: '',
      loginFailed: false,
    };
  },
  methods: {
    mostrarLogin() {
      this.loginVisible = true;
    },
    async login() {
      try {
        const response = await apiLogin(this.usuario, this.password);
        localStorage.setItem("accessToken", response.access);
        localStorage.setItem("user", JSON.stringify(response));
        this.$emit('login');
        this.loginFailed = false;
        this.$router.push('/');
      } catch (err) {
        this.loginFailed = true;
        console.error("Error de login:", err);
      }
    },
    irRegistrarUsuario() {
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
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -1;
}

/* Contenedor que centra todo y pone los logos a los lados */
.login-wrapper {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(16px, 4vw, 48px);
  padding-inline: clamp(12px, 4vw, 48px);
}

/* Cuadro de login */
.login-form {
  background-color: rgba(255, 255, 255, 0.9);
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  z-index: 1;
  width: min(92vw, 420px);
}

.login-form h2 {
  text-align: center;
  margin-bottom: 20px;
}

.login-form form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.login-form label {
  font-weight: 600;
}

.login-form input {
  padding: 10px 12px;
  border: 1px solid #d8d8d8;
  border-radius: 8px;
  outline: none;
}

.login-form input:focus {
  border-color: #8d2a2a;
  box-shadow: 0 0 0 3px rgba(141, 42, 42, 0.15);
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
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
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
  color: #d11;
  text-align: center;
  margin-top: 6px;
}

/* Logos laterales */
.side-logo {
  max-height: clamp(64px, 18vh, 140px);
  width: auto;
  object-fit: contain;
  user-select: none;
  pointer-events: none;
  filter: drop-shadow(0 2px 6px rgba(0,0,0,.25));
}

/* Alineación explícita por si necesitas estilos distintos por lado */
.side-logo-left { }
.side-logo-right { }

/* Responsivo: en tablets reduce tamaño; en móviles muy angostos oculta logos */
@media (max-width: 900px) {
  .side-logo {
    max-height: clamp(56px, 14vh, 110px);
  }
}

@media (max-width: 640px) {
  .login-wrapper {
    gap: 12px;
  }
  .side-logo {
    display: none; /* Oculta en pantallas muy pequeñas para priorizar el formulario */
  }
}
</style>
