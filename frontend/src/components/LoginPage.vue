<template>
  <div class="login-container">
    <!-- (Opcional) Video de fondo 
    <video autoplay muted playsinline preload="none" poster="" class="video-fondo">
      <source src="@/assets/Diseño sin título.mp4" type="video/mp4" />
      Tu navegador no soporta el elemento de video.
    </video>
    -->

    <!-- Barra superior -->
    <header class="topbar">
      <div class="brand" @click="setTab('inicio')" role="button" tabindex="0">
        <img src="@/assets/ipnlogo.png" alt="IPN" class="brand-logo" draggable="false" />
        <span class="brand-name">AppQuaculture</span>
      </div>

      <nav class="main-nav" aria-label="Navegación principal">
        <button
          v-for="item in navItems"
          :key="item.key"
          :class="['nav-link', { active: currentTab === item.key }]"
          @click="setTab(item.key)"
        >
          <span class="nav-icon" aria-hidden="true">{{ item.icon }}</span>
          {{ item.label }}
        </button>
      </nav>
    </header>

    <!-- Contenido -->
    <div class="content-wrapper">
      <!-- Logos laterales (en escritorio) -->
      <img
        class="side-logo side-logo-left"
        src="@/assets/ipnlogo.png"
        alt="Logo del IPN"
        draggable="false"
      />
      <img
        class="side-logo side-logo-right"
        src="@/assets/ciidirlogo.png"
        alt="Logo de CIIDIR"
        draggable="false"
      />

      <!-- Contenido por pestaña -->
      <section class="panel" v-if="currentTab === 'inicio'">
        <div class="hero">
          <h1>Gestión acuícola, clara y a tu alcance</h1>
          <p class="sub">
            Monitorea crecimiento, calidad de agua y costos en un solo lugar.
            Optimiza ciclos, reportes y toma decisiones con datos reales.
          </p>

          <div class="hero-cta">
            <button class="btn btn-primary" @click="setTab('login')">Iniciar sesión</button>
            <button class="btn btn-ghost" @click="setTab('registro')">Crear cuenta</button>
          </div>

          <ul class="features">
            <li>
              <h3>📈 Crecimiento</h3>
              <p>Visualiza promedios por fecha y distribución de tallas por ciclo.</p>
            </li>
            <li>
              <h3>💧 Calidad de agua</h3>
              <p>Gráficos legibles, PDF con tablas y pie de página institucional.</p>
            </li>
            <li>
              <h3>💸 Costos operativos</h3>
              <p>Gastos generales y por ciclo para calcular el costo total.</p>
            </li>
            <li>
              <h3>🧪 ANOVA y normalidad</h3>
              <p>Pruebas KS y Shapiro–Wilk con exportación a PDF y Excel.</p>
            </li>
          </ul>
        </div>
      </section>

      <section class="panel" v-else-if="currentTab === 'login'">
        <!-- Formulario de login (misma lógica, estética mejorada) -->
        <div class="login-form" role="form" aria-labelledby="login-title">
          <h2 id="login-title">Iniciar sesión</h2>
          <form @submit.prevent="login" novalidate>
            <label for="usuario">Usuario</label>
            <input
              type="text"
              id="usuario"
              name="usuario"
              v-model.trim="usuario"
              required
              autocomplete="username"
              spellcheck="false"
            />

            <label for="password">Contraseña</label>
            <input
              type="password"
              id="password"
              name="password"
              v-model="password"
              required
              autocomplete="current-password"
            />

            <div class="buttons">
              <button type="submit" class="btn btn-primary">Iniciar sesión</button>
              <div class="inline-links">
                <a href="#" @click.prevent="setTab('recuperar')">¿Olvidaste tu contraseña?</a>
                <a href="#" @click.prevent="setTab('registro')">Registrarse</a>
              </div>
            </div>

            <p v-if="loginFailed" class="error-message" role="alert" aria-live="assertive">
              Usuario o contraseña incorrectos.
            </p>
          </form>
        </div>
      </section>

      <section class="panel" v-else-if="currentTab === 'registro'">
        <!-- Registro (estético, sin tocar backend) -->
        <div class="form-card" role="form" aria-labelledby="reg-title">
          <h2 id="reg-title">Crear cuenta</h2>
          <form @submit.prevent="mockSubmit('registro')" novalidate>
            <div class="grid-2">
              <div>
                <label for="nombre">Nombre</label>
                <input id="nombre" v-model.trim="reg.nombre" type="text" required />
              </div>
              <div>
                <label for="apellido">Apellido</label>
                <input id="apellido" v-model.trim="reg.apellido" type="text" required />
              </div>
            </div>

            <label for="email">Correo</label>
            <input id="email" v-model.trim="reg.email" type="email" required autocomplete="email" />

            <label for="usuario_reg">Usuario</label>
            <input id="usuario_reg" v-model.trim="reg.usuario" type="text" required autocomplete="username" />

            <div class="grid-2">
              <div>
                <label for="pass_reg">Contraseña</label>
                <input id="pass_reg" v-model="reg.password" type="password" required autocomplete="new-password" />
              </div>
              <div>
                <label for="pass2_reg">Confirmar contraseña</label>
                <input id="pass2_reg" v-model="reg.password2" type="password" required autocomplete="new-password" />
              </div>
            </div>

            <button type="submit" class="btn btn-primary">Crear cuenta</button>
            <p class="muted">Al registrarte aceptas los términos y políticas.</p>
          </form>
        </div>
      </section>

      <section class="panel" v-else-if="currentTab === 'contacto'">
        <!-- Contacto -->
        <div class="form-card" role="form" aria-labelledby="contact-title">
          <h2 id="contact-title">Contacto</h2>
          <form @submit.prevent="mockSubmit('contacto')" novalidate>
            <label for="c-nombre">Nombre</label>
            <input id="c-nombre" v-model.trim="contacto.nombre" type="text" required />

            <label for="c-email">Correo</label>
            <input id="c-email" v-model.trim="contacto.email" type="email" required autocomplete="email" />

            <label for="c-asunto">Asunto</label>
            <input id="c-asunto" v-model.trim="contacto.asunto" type="text" required />

            <label for="c-msj">Mensaje</label>
            <textarea id="c-msj" v-model.trim="contacto.mensaje" rows="4" required></textarea>

            <button type="submit" class="btn btn-primary">Enviar</button>
            <p class="muted">También puedes escribirnos a: contacto@appquaculture.mx</p>
          </form>
        </div>
      </section>

      <section class="panel" v-else-if="currentTab === 'acerca'">
        <!-- Acerca -->
        <div class="about">
          <h2>Acerca de AppQuaculture</h2>
          <p>
            Proyecto académico–productivo desarrollado en CIIDIR–IPN y comunidad local, enfocado en la
            gestión integral de granjas acuícolas. Integra módulos de siembra, crecimiento, calidad de
            agua, costos y reportes científicos (KS, Shapiro–Wilk, ANOVA).
          </p>

          <div class="stats">
            <div>
              <h3>+3,500</h3>
              <p>registros de mediciones</p>
            </div>
            <div>
              <h3>4</h3>
              <p>módulos analíticos</p>
            </div>
            <div>
              <h3>PDF/Excel</h3>
              <p>exportaciones listas</p>
            </div>
          </div>

          <div class="about-cta">
            <button class="btn btn-ghost" @click="setTab('contacto')">Contáctanos</button>
            <button class="btn btn-primary" @click="setTab('login')">Comenzar ahora</button>
          </div>
        </div>
      </section>

      <section class="panel" v-else-if="currentTab === 'recuperar'">
        <!-- Recuperar contraseña (UI estética) -->
        <div class="form-card" role="form" aria-labelledby="rec-title">
          <h2 id="rec-title">Recuperar contraseña</h2>
          <form @submit.prevent="mockSubmit('recuperar')" novalidate>
            <label for="rec-email">Correo de la cuenta</label>
            <input id="rec-email" v-model.trim="recuperar.email" type="email" required autocomplete="email" />
            <button type="submit" class="btn btn-primary">Enviar enlace</button>
            <p class="muted">
              Te enviaremos instrucciones si el correo está asociado a una cuenta.
            </p>
          </form>
        </div>
      </section>
    </div>

    <!-- Pie -->
    <footer class="footer">
      <div>© {{ new Date().getFullYear() }} AppQuaculture · CIIDIR–IPN</div>
      <div class="footer-links">
        <a href="#" @click.prevent="setTab('acerca')">Acerca</a>
        <a href="#" @click.prevent="setTab('contacto')">Contacto</a>
        <a href="#" @click.prevent="setTab('registro')">Crear cuenta</a>
      </div>
    </footer>
  </div>
</template>

<script>
import { login as apiLogin } from '@/services/auth';

export default {
  name: "LoginPage",
  data() {
    return {
      // Navegación interna
      currentTab: 'inicio',
      navItems: [
        { key: 'inicio',   label: 'Inicio',          icon: '🏠' },
        { key: 'login',    label: 'Iniciar sesión',  icon: '🔐' },
        { key: 'registro', label: 'Registro',        icon: '📝' },
        { key: 'contacto', label: 'Contacto',        icon: '✉️' },
        { key: 'acerca',   label: 'Acerca',          icon: 'ℹ️' },
      ],

      // Login (sin cambios de flujo)
      usuario: '',
      password: '',
      loginFailed: false,

      // UI formularios
      reg: {
        nombre: '',
        apellido: '',
        email: '',
        usuario: '',
        password: '',
        password2: '',
      },
      contacto: {
        nombre: '',
        email: '',
        asunto: '',
        mensaje: '',
      },
      recuperar: {
        email: '',
      },
    };
  },
  methods: {
    setTab(key) {
      this.currentTab = key;
      // scroll suave al contenido
      try {
        const el = document.querySelector('.content-wrapper');
        el && el.scrollTo({ top: 0, behavior: 'smooth' });
      } catch {}
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
    mockSubmit(tipo) {
      // Solo estética. Aquí podrías abrir un modal o notificación.
      if (tipo === 'registro') {
        if (!this.reg.nombre || !this.reg.apellido || !this.reg.email || !this.reg.usuario || !this.reg.password || !this.reg.password2) {
          alert('Completa todos los campos.');
          return;
        }
        if (this.reg.password !== this.reg.password2) {
          alert('Las contraseñas no coinciden.');
          return;
        }
        alert('Registro enviado (demo UI).');
        this.setTab('login');
      } else if (tipo === 'contacto') {
        if (!this.contacto.nombre || !this.contacto.email || !this.contacto.asunto || !this.contacto.mensaje) {
          alert('Completa todos los campos.');
          return;
        }
        alert('Mensaje enviado (demo UI). ¡Gracias por contactarnos!');
        this.contacto = { nombre:'', email:'', asunto:'', mensaje:'' };
      } else if (tipo === 'recuperar') {
        if (!this.recuperar.email) {
          alert('Ingresa tu correo.');
          return;
        }
        alert('Si el correo existe, recibirás un enlace (demo UI).');
        this.setTab('login');
      }
    },
  },
}
</script>

<style scoped>
/* Layout base */
.login-container {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(141,42,42,.10), transparent 50%),
    radial-gradient(800px 400px at 110% 10%, rgba(141,42,42,.08), transparent 50%),
    linear-gradient(180deg, #f6f6f6, #fafafa);
  color: #222;
}

.video-fondo {
  position: fixed;
  inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  z-index: -1;
  filter: contrast(1.05) saturate(1.02);
}

/* Topbar */
.topbar {
  position: sticky;
  top: 0;
  z-index: 5;
  backdrop-filter: blur(8px);
  background: rgba(255,255,255,.75);
  border-bottom: 1px solid rgba(0,0,0,.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px clamp(12px, 4vw, 28px);
}

.brand {
  display: flex; align-items: center; gap: 10px;
  user-select: none;
}
.brand:focus { outline: 2px solid #8d2a2a33; outline-offset: 4px; }
.brand-logo { height: 34px; width: auto; filter: drop-shadow(0 1px 3px rgba(0,0,0,.15)); }
.brand-name { font-weight: 800; letter-spacing: .2px; color: #8d2a2a; }

.main-nav { display: flex; gap: clamp(6px, 2vw, 12px); flex-wrap: wrap; }
.nav-link {
  position: relative;
  border: 0; background: transparent; cursor: pointer;
  font-weight: 700; padding: 8px 12px; border-radius: 10px;
  color: #583a34;
  transition: transform .08s ease, background .2s ease, color .2s ease;
}
.nav-link .nav-icon { margin-right: 6px; }
.nav-link:hover { background: rgba(141,42,42,.08); color: #8d2a2a; }
.nav-link.active { background: rgba(141,42,42,.12); color: #8d2a2a; box-shadow: inset 0 0 0 1px rgba(141,42,42,.25); }

/* Contenido central */
.content-wrapper {
  position: relative;
  max-width: 1100px;
  margin: 32px auto;
  padding: 0 clamp(12px, 4vw, 28px);
  display: grid;
  grid-template-columns: 1fr;
  place-items: center;
}

/* Tarjetas/paneles */
.panel {
  background: rgba(255,255,255,.92);
  width: min(100%, 980px);
  border-radius: 16px;
  padding: clamp(18px, 3.2vw, 32px);
  box-shadow: 0 10px 30px rgba(0,0,0,.08);
  position: relative;
  z-index: 1;
}

/* Hero de Inicio */
.hero { text-align: center; }
.hero h1 {
  font-size: clamp(1.6rem, 3.4vw, 2.2rem);
  line-height: 1.2;
  margin-bottom: 8px;
}
.sub { color: #5a3d31; max-width: 760px; margin: 0 auto 18px; }
.hero-cta { display: flex; gap: 12px; justify-content: center; margin-bottom: 10px; }

.features {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: clamp(10px, 2.4vw, 18px);
  margin-top: 18px;
}
.features li {
  list-style: none;
  background: #fff;
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 14px;
  padding: 14px;
  text-align: left;
  box-shadow: 0 6px 18px rgba(0,0,0,.05);
}
.features h3 { margin-bottom: 6px; font-size: 1rem; }
@media (max-width: 900px) { .features { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 520px) { .features { grid-template-columns: 1fr; } }

/* Formularios */
.login-form, .form-card {
  background-color: rgba(255,255,255, 0.96);
  padding: clamp(18px, 3vw, 28px);
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.10);
  width: min(92vw, 520px);
  margin: 0 auto;
}
.login-form h2, .form-card h2 { text-align: center; margin-bottom: 14px; }
.login-form form, .form-card form { display: flex; flex-direction: column; gap: 12px; }
label { font-weight: 700; color: #3b2c27; }
input, textarea {
  padding: 10px 12px; border: 1px solid #d8d8d8; border-radius: 10px; outline: none;
  background: #fff;
}
input:focus, textarea:focus {
  border-color: #8d2a2a;
  box-shadow: 0 0 0 3px rgba(141, 42, 42, 0.15);
}

.grid-2 {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
}
@media (max-width: 560px) { .grid-2 { grid-template-columns: 1fr; } }

.buttons { display: flex; flex-direction: column; gap: 10px; }
.inline-links { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.inline-links a {
  text-align: center; color: #8d2a2a; text-decoration: none; font-weight: 700; cursor: pointer;
}

.error-message { color: #c22; text-align: center; margin-top: 2px; }

/* Botones */
.btn {
  padding: 10px 14px; border-radius: 10px; border: none; cursor: pointer; font-weight: 800;
  transition: transform .06s ease, box-shadow .2s ease, background .2s ease, color .2s ease;
}
.btn:active { transform: translateY(1px); }
.btn-primary {
  background-color: #8d2a2a; color: #fff;
  box-shadow: 0 8px 18px rgba(141,42,42,.25);
}
.btn-primary:hover { background-color: #7b2323; box-shadow: 0 10px 20px rgba(141,42,42,.28); }
.btn-ghost {
  background: transparent; color: #8d2a2a; box-shadow: inset 0 0 0 1px rgba(141,42,42,.35);
}
.btn-ghost:hover { background: rgba(141,42,42,.08); }

/* Acerca */
.about h2 { text-align: center; margin-bottom: 10px; }
.about p { color: #5a3d31; max-width: 740px; margin: 0 auto 18px; text-align: center; }
.stats {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
  margin: 10px auto 2px; max-width: 720px;
}
.stats > div { background: #fff; border: 1px solid rgba(0,0,0,.06); border-radius: 14px; padding: 14px; text-align: center; }
.stats h3 { margin: 0; color: #8d2a2a; font-size: 1.2rem; }
.stats p { margin: 4px 0 0; color: #5a3d31; }

/* Logos laterales */
.side-logo {
  position: absolute; top: 120px;
  max-height: clamp(64px, 18vh, 140px);
  width: auto; object-fit: contain; user-select: none; pointer-events: none;
  filter: drop-shadow(0 2px 6px rgba(0,0,0,.25));
}
.side-logo-left  { left: 24px; }
.side-logo-right { right: 24px; }

@media (max-width: 900px) {
  .side-logo { max-height: clamp(56px, 14vh, 110px); }
}
@media (max-width: 820px) {
  .side-logo { display: none; }
}

/* Footer */
.footer {
  margin: 22px auto 10px;
  padding: 8px clamp(12px, 4vw, 28px);
  max-width: 1100px;
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  color: #6b524b;
}
.footer-links { display: flex; gap: 12px; flex-wrap: wrap; }
.footer a { color: #8d2a2a; text-decoration: none; font-weight: 700; }

/* Selección de texto y scrollbars suaves */
::selection { background: rgba(141,42,42,.2); }
</style>
