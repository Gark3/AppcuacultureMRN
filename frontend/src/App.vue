<template>
  <div>
    <!-- Rutas de autenticación -->
    <div v-if="isAuthRoute">
      <router-view />
    </div>

    <!-- Layout general (usuario logueado) -->
    <div v-else-if="loggedIn" class="app-shell">
      <!-- Header superior -->
      <header class="header">
        <div class="header-left">
          <button class="hamburger" @click="toggleMenu" aria-label="Toggle menu" :aria-expanded="isMenuOpen">☰</button>
          <img class="brand" src="@/assets/AppQuacultureLogo.png" alt="AppQuaculture" />
        </div>

        <nav class="menu-buttons">
          <button
            v-for="item in menuItems"
            :key="item"
            @click="changeMenu(item)"
            :class="{ active: currentMenu === item }"
            :title="`Cambia a la sección ${item}`"
          >
            {{ item }}
          </button>
        </nav>
      </header>

      <div class="main-container">
        <!-- Menú lateral -->
        <aside
          class="side-menu"
          :class="{
            'open': isMenuOpen,
          }"
        >
          <div class="side-header">
            <span class="side-title">{{ currentMenu || 'Menú' }}</span>
            <button class="side-close" @click="closeMenu" aria-label="Cerrar menú">✕</button>
          </div>

          <ul class="side-list">
            <!-- Submenú: Producción -->
            <template v-if="currentMenu === 'Producción'">
              <li><router-link to="/producción/agregar-estanque" class="side-menu-link" @click="onNavClick">Agregar Estanque</router-link></li>
              <li><router-link to="/producción/siembra" class="side-menu-link" @click="onNavClick">Siembra</router-link></li>
              <li><router-link to="/producción/alimentar" class="side-menu-link" @click="onNavClick">Alimentar</router-link></li>
              <li><router-link to="/producción/calidad-agua" class="side-menu-link" @click="onNavClick">Calidad AGUA</router-link></li>
              <li><router-link to="/producción/dieta" class="side-menu-link" @click="onNavClick">Dieta</router-link></li>
              <li><router-link to="/producción/crecimiento" class="side-menu-link" @click="onNavClick">Crecimiento</router-link></li>
              <li><router-link to="/producción/cosecha" class="side-menu-link" @click="onNavClick">Cosecha</router-link></li>
              <li><router-link to="/producción/tratamientos" class="side-menu-link" @click="onNavClick">Tratamientos</router-link></li>
              <li><router-link to="/producción/cuarentena" class="side-menu-link" @click="onNavClick">Cuarentena</router-link></li>
            </template>

            <!-- Submenú: Reporte -->
            <template v-else-if="currentMenu === 'Reporte'">
              <li><router-link to="/reporte/estanque" class="side-menu-link" @click="onNavClick">Estanque</router-link></li>
              <li><router-link to="/reporte/crecimiento" class="side-menu-link" @click="onNavClick">Crecimiento</router-link></li>
              <li><router-link to="/reporte/gpc" class="side-menu-link" @click="onNavClick">GPC</router-link></li>
              <li><router-link to="/reporte/calidad-agua" class="side-menu-link" @click="onNavClick">Calidad AGUA</router-link></li>
            </template>

            <!-- Submenú: Almacén -->
            <template v-else-if="currentMenu === 'Almacén'">
              <li><router-link to="/almacén/inventario" class="side-menu-link" @click="onNavClick">Inventario</router-link></li>
              <li><router-link to="/almacén/proveedores" class="side-menu-link" @click="onNavClick">Proveedores</router-link></li>
              <li><router-link to="/almacén/alta-material" class="side-menu-link" @click="onNavClick">Alta Material</router-link></li>
              <li><router-link to="/almacén/alta-proveedores" class="side-menu-link" @click="onNavClick">Alta Proveedores</router-link></li>
              <li><router-link to="/almacén/entradas" class="side-menu-link" @click="onNavClick">Entradas</router-link></li>
              <li><router-link to="/almacén/salidas" class="side-menu-link" @click="onNavClick">Salidas</router-link></li>
              <li><router-link to="/almacén/inventario-fisico" class="side-menu-link" @click="onNavClick">Inventario Físico</router-link></li>
            </template>

            <!-- Submenú: Estadístico -->
            <template v-else-if="currentMenu === 'Estadístico'">
              <li><router-link to="/estadístico/kolmogorov-smirnov" class="side-menu-link" @click="onNavClick">Kolmogorov-Smirnov</router-link></li>
              <li><router-link to="/estadístico/shapiro-wilk" class="side-menu-link" @click="onNavClick">Shapiro-Wilk</router-link></li>
              <li><router-link to="/estadístico/anova" class="side-menu-link" @click="onNavClick">ANOVA</router-link></li>
            </template>

            <!-- Submenú: Contaduría -->
            <template v-else-if="currentMenu === 'Contaduría'">
              <li><router-link to="/contaduría/nomina" class="side-menu-link" @click="onNavClick">Nomina</router-link></li>
              <li><router-link to="/contaduría/sueldos" class="side-menu-link" @click="onNavClick">Salarios</router-link></li>
              <li><router-link to="/contaduría/pagos-servicios" class="side-menu-link" @click="onNavClick">Pagos Servicios</router-link></li>
              <li><router-link to="/contaduría/compras" class="side-menu-link" @click="onNavClick">Compras</router-link></li>
              <li><router-link to="/contaduría/mantenimiento" class="side-menu-link" @click="onNavClick">Mantenimiento</router-link></li>
              <li><router-link to="/contaduría/costos-operativos" class="side-menu-link" @click="onNavClick">Costos Operativos</router-link></li>
              <li><router-link to="/contaduría/ventas" class="side-menu-link" @click="onNavClick">Ventas</router-link></li>
            </template>

            <!-- Submenú vacío -->
            <template v-else>
              <li class="side-empty">Selecciona una sección arriba</li>
            </template>
          </ul>
        </aside>

        <!-- Overlay (solo móvil/tablet) -->
        <div v-if="isOverlayMode && isMenuOpen" class="overlay" @click="closeMenu"></div>

        <!-- Contenido -->
        <main class="content" :class="{ 'with-aside': !isOverlayMode && isMenuOpen }">
          <router-view />
        </main>
      </div>
    </div>

    <!-- Login si no está logueado -->
    <div v-else>
      <Login @login="onLogin" />
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Login from "@/components/LoginPage.vue";

export default {
  name: "App",
  components: { Login },
  data() {
    return {
      loggedIn: false,
      currentMenu: "Producción",
      menuItems: ["Producción", "Reporte", "Almacén", "Estadístico", "Contaduría", "Cuenta"],
      isMenuOpen: false,
      viewportWidth: window.innerWidth,
      overlayBreakpoint: 1024, // < 1024 => overlay (móvil/tablet)
      // Mapa de rutas “raíces” sin acentos
      menuRouteMap: {
        "Producción": "/produccion",
        "Reporte": "/reporte",
        "Almacén": "/almacen",
        "Estadístico": "/estadistico",
        "Contaduría": "/contaduria",
        "Cuenta": "/cuenta",
      },
    };
  },
  computed: {
    // rutas de autenticación
    isAuthRoute() {
      const path = this.$route.path;
      return path === "/login" || path === "/registrarusuario";
    },
    // modo overlay depende del ancho
    isOverlayMode() {
      return this.viewportWidth < this.overlayBreakpoint;
    },
  },
  methods: {
    onLogin() {
      this.loggedIn = true;
      this.configurarToken();
    },
    changeMenu(menuItem) {
      this.currentMenu = menuItem;
      // SIEMPRE abrir el lateral al elegir un menú (desktop y móvil)
      this.isMenuOpen = true;

      // Navegar a raíz del menú (opcional)
      const route = this.menuRouteMap[menuItem];
      if (route && this.$route.path !== route) {
        this.$router.push(route);
      }
    },
    onNavClick() {
      // Si estás en móvil/tablet, cerrar el overlay al seleccionar una opción
      if (this.isOverlayMode) this.closeMenu();
    },
    openMenu() { this.isMenuOpen = true; },
    closeMenu() { this.isMenuOpen = false; },
    toggleMenu() { this.isMenuOpen = !this.isMenuOpen; },
    configurarToken() {
      const token = localStorage.getItem("accessToken");
      if (token) axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      else delete axios.defaults.headers.common["Authorization"];
    },
    onResize() {
      this.viewportWidth = window.innerWidth;
      // En desktop mantenemos abierto por UX
      if (!this.isOverlayMode) this.isMenuOpen = true;
    },
  },
  created() {
    this.configurarToken();
    // Estado inicial según viewport
    this.isMenuOpen = window.innerWidth >= this.overlayBreakpoint;
  },
  mounted() {
    window.addEventListener("resize", this.onResize);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.onResize);
  },
};
</script>

<style>
/* Base */
:root { --header-h: 64px; }
html, body, #app { height: 100%; }
body {
  font-family: "Poppins", sans-serif;
  margin: 0; padding: 0;
  background-color: #f8f9fa; color: #333;
}
.app-shell { display: flex; flex-direction: column; min-height: 100vh; }

/* Header superior */
.header {
  background-color: #007bff; color: white;
  padding: 12px 16px;
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 4px 8px rgba(0,0,0,.08);
  position: sticky; top: 0; z-index: 50;
  min-height: var(--header-h);
}
.header-left { display: flex; align-items: center; gap: 12px; }
.brand { width: 44px; height: 44px; object-fit: contain; }
.hamburger {
  background: #005fcc; color: #fff; border: none; border-radius: 8px;
  font-size: 20px; padding: 8px 10px; cursor: pointer;
  transition: background .2s ease, transform .1s ease;
}
.hamburger:hover { background: #004fa9; transform: translateY(-1px); }

.menu-buttons { display: flex; gap: 6px; flex-wrap: wrap; }
.menu-buttons button {
  background: transparent; border: none; color: white; font-weight: 600;
  padding: 8px 10px; border-radius: 6px; cursor: pointer; transition: background .2s ease;
}
.menu-buttons button:hover { background: rgba(255,255,255,.15); }
.menu-buttons .active { background: #ffc107; color: #1f2937; }

/* Contenedor principal */
.main-container {
  position: relative;
  flex: 1;
  min-height: 0;
}

/* Aside lateral */
.side-menu {
  position: fixed;
  top: var(--header-h);
  left: 0; bottom: 0;
  width: 260px;
  background: #343a40; color: white;
  transform: translateX(-100%); /* oculto */
  transition: transform .25s ease;
  z-index: 60;
  overflow-y: auto;
  box-shadow: 2px 0 8px rgba(0,0,0,.2);
}
.side-menu.open { transform: translateX(0); }

/* Header del aside */
.side-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; background: #2c3136; position: sticky; top: 0;
}
.side-title { font-weight: 600; }
.side-close {
  background: transparent; color: #e5e7eb; border: none; cursor: pointer;
  font-size: 18px; border-radius: 6px;
}
.side-close:hover { background: rgba(255,255,255,.08); }

/* Lista aside */
.side-list { list-style: none; padding: 10px; margin: 0; }
.side-empty { opacity: .8; padding: 8px 10px; }
.side-menu-link {
  display: block; color: white; text-decoration: none;
  padding: 10px 12px; border-radius: 6px; transition: background .2s ease;
}
.side-menu-link:hover { background: #495057; }

/* Overlay (solo móvil/tablet) */
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.4);
  z-index: 55;
}

/* Contenido */
.content {
  min-height: calc(100vh - var(--header-h));
  padding: 20px; background: white;
  width: 100%;
  box-sizing: border-box;
  transition: padding-left .25s ease;
}
/* En desktop el contenido se desplaza cuando el aside está abierto */
@media (min-width: 1024px) {
  .content.with-aside { padding-left: 260px; }
}
</style>
