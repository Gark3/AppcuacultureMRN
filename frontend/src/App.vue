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
            v-for="item in visibleMenuItems"
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
        <aside class="side-menu" :class="{ 'open': isMenuOpen }">
          <div class="side-header">
            <span class="side-title">{{ currentMenu || 'Menú' }}</span>
            <button class="side-close" @click="closeMenu" aria-label="Cerrar menú">✕</button>
          </div>

          <ul class="side-list" v-if="!loadingPerms">
            <!-- Submenú: Producción -->
            <template v-if="currentMenu === 'Producción' && can('menu_produccion')">
              <!-- NUEVO: Proyección hereda del permiso de 'agregar estanque' mediante alias -->
              <li v-if="has('produccion_proyeccion')">
                <router-link to="/produccion/proyeccion" class="side-menu-link" @click="onNavClick">Proyección</router-link>
              </li>

              <li v-if="has('produccion_agregar_estanque')">
                <router-link to="/producción/agregar-estanque" class="side-menu-link" @click="onNavClick">Agregar Estanque</router-link>
              </li>
              <li v-if="has('produccion_siembra')">
                <router-link to="/producción/siembra" class="side-menu-link" @click="onNavClick">Siembra</router-link>
              </li>
              <li v-if="has('produccion_alimentar')">
                <router-link to="/producción/alimentar" class="side-menu-link" @click="onNavClick">Alimentar</router-link>
              </li>
              <li v-if="has('produccion_calidad_agua')">
                <router-link to="/producción/calidad-agua" class="side-menu-link" @click="onNavClick">Calidad AGUA</router-link>
              </li>
              <li v-if="has('produccion_dieta')">
                <router-link to="/producción/dieta" class="side-menu-link" @click="onNavClick">Dieta</router-link>
              </li>
              <li v-if="has('produccion_crecimiento')">
                <router-link to="/producción/crecimiento" class="side-menu-link" @click="onNavClick">Crecimiento</router-link>
              </li>
              <li v-if="has('produccion_cosecha')">
                <router-link to="/producción/cosecha" class="side-menu-link" @click="onNavClick">Cosecha</router-link>
              </li>
              <li v-if="has('produccion_tratamientos')">
                <router-link to="/producción/tratamientos" class="side-menu-link" @click="onNavClick">Tratamientos</router-link>
              </li>
              <li v-if="has('produccion_cuarentena')">
                <router-link to="/producción/cuarentena" class="side-menu-link" @click="onNavClick">Cuarentena</router-link>
              </li>
            </template>

            <!-- Submenú: Reporte -->
            <template v-else-if="currentMenu === 'Reporte' && can('menu_reporte')">
              <li v-if="has('reporte_estanque')">
                <router-link to="/reporte/estanque" class="side-menu-link" @click="onNavClick">Estanque</router-link>
              </li>
              <li v-if="has('reporte_crecimiento')">
                <router-link to="/reporte/crecimiento" class="side-menu-link" @click="onNavClick">Crecimiento</router-link>
              </li>
              <li v-if="has('reporte_gpc')">
                <router-link to="/reporte/gpc" class="side-menu-link" @click="onNavClick">GPC</router-link>
              </li>
              <li v-if="has('reporte_calidad_agua')">
                <router-link to="/reporte/calidad-agua" class="side-menu-link" @click="onNavClick">Calidad AGUA</router-link>
              </li>
            </template>

            <!-- Submenú: Almacén -->
            <template v-else-if="currentMenu === 'Almacén' && can('menu_almacen')">
              <li v-if="has('almacen_inventario')">
                <router-link to="/almacén/inventario" class="side-menu-link" @click="onNavClick">Inventario</router-link>
              </li>
              <li v-if="has('almacen_proveedores')">
                <router-link to="/almacén/proveedores" class="side-menu-link" @click="onNavClick">Proveedores</router-link>
              </li>
              <li v-if="has('almacen_alta_material')">
                <router-link to="/almacén/alta-material" class="side-menu-link" @click="onNavClick">Alta Material</router-link>
              </li>
              <li v-if="has('almacen_alta_proveedores')">
                <router-link to="/almacén/alta-proveedores" class="side-menu-link" @click="onNavClick">Alta Proveedores</router-link>
              </li>
              <li v-if="has('almacen_entradas')">
                <router-link to="/almacén/entradas" class="side-menu-link" @click="onNavClick">Entradas</router-link>
              </li>
              <li v-if="has('almacen_salidas')">
                <router-link to="/almacén/salidas" class="side-menu-link" @click="onNavClick">Salidas</router-link>
              </li>
              <li v-if="has('almacen_inventario_fisico')">
                <router-link to="/almacén/inventario-fisico" class="side-menu-link" @click="onNavClick">Inventario Físico</router-link>
              </li>
            </template>

            <!-- Submenú: Estadístico -->
            <template v-else-if="currentMenu === 'Estadístico' && can('menu_estadistico')">
              <li v-if="has('estadistico_kolmogorov_smirnov')">
                <router-link to="/estadístico/kolmogorov-smirnov" class="side-menu-link" @click="onNavClick">Kolmogorov-Smirnov</router-link>
              </li>
              <li v-if="has('estadistico_shapiro_wilk')">
                <router-link to="/estadístico/shapiro-wilk" class="side-menu-link" @click="onNavClick">Shapiro-Wilk</router-link>
              </li>
              <li v-if="has('estadistico_anova')">
                <router-link to="/estadístico/anova" class="side-menu-link" @click="onNavClick">ANOVA</router-link>
              </li>
            </template>

            <!-- Submenú: Contaduría -->
            <template v-else-if="currentMenu === 'Contaduría' && can('menu_contaduria')">
              <li v-if="has('contaduria_nomina')">
                <router-link to="/contaduría/nomina" class="side-menu-link" @click="onNavClick">Nomina</router-link>
              </li>
              <li v-if="has('contaduria_sueldos')">
                <router-link to="/contaduría/sueldos" class="side-menu-link" @click="onNavClick">Salarios</router-link>
              </li>
              <li v-if="has('contaduria_pagos_servicios')">
                <router-link to="/contaduría/pagos-servicios" class="side-menu-link" @click="onNavClick">Pagos Servicios</router-link>
              </li>
              <li v-if="has('contaduria_compras')">
                <router-link to="/contaduría/compras" class="side-menu-link" @click="onNavClick">Compras</router-link>
              </li>
              <li v-if="has('contaduria_mantenimiento')">
                <router-link to="/contaduría/mantenimiento" class="side-menu-link" @click="onNavClick">Mantenimiento</router-link>
              </li>
              <li v-if="has('contaduria_costos_operativos')">
                <router-link to="/contaduría/costos-operativos" class="side-menu-link" @click="onNavClick">Costos Operativos</router-link>
              </li>
              <li v-if="has('contaduria_ventas')">
                <router-link to="/contaduría/ventas" class="side-menu-link" @click="onNavClick">Ventas</router-link>
              </li>
            </template>

            <!-- Cuenta -->
            <template v-else-if="currentMenu === 'Cuenta'">
              <li>
                <button class="side-menu-link" @click="logout">Cerrar sesión</button>
              </li>
            </template>

            <!-- Submenú vacío -->
            <template v-else>
              <li class="side-empty">Selecciona una sección arriba</li>
            </template>
          </ul>

          <ul class="side-list" v-else>
            <li class="side-empty">Cargando permisos…</li>
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

const DEFAULT_PERMS = {
  // Menús
  menu_produccion: false,
  menu_reporte: false,
  menu_almacen: false,
  menu_estadistico: false,
  menu_contaduria: false,
  // Producción
  produccion_agregar_estanque: false,
  produccion_siembra: false,
  produccion_alimentar: false,
  produccion_calidad_agua: false,
  produccion_dieta: false,
  produccion_crecimiento: false,
  produccion_cosecha: false,
  produccion_tratamientos: false,
  produccion_cuarentena: false,
  // Reporte
  reporte_estanque: false,
  reporte_crecimiento: false,
  reporte_gpc: false,
  reporte_calidad_agua: false,
  // Almacén
  almacen_inventario: false,
  almacen_proveedores: false,
  almacen_alta_material: false,
  almacen_alta_proveedores: false,
  almacen_entradas: false,
  almacen_salidas: false,
  almacen_inventario_fisico: false,
  // Estadístico
  estadistico_kolmogorov_smirnov: false,
  estadistico_shapiro_wilk: false,
  estadistico_anova: false,
  // Contaduría
  contaduria_nomina: false,
  contaduria_sueldos: false,
  contaduria_pagos_servicios: false,
  contaduria_compras: false,
  contaduria_mantenimiento: false,
  contaduria_costos_operativos: false,
  contaduria_ventas: false,
};

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
      overlayBreakpoint: 1024,
      // Rutas raíz sin acentos
      menuRouteMap: {
        "Producción": "/produccion",
        "Reporte": "/reporte",
        "Almacén": "/almacen",
        "Estadístico": "/estadistico",
        "Contaduría": "/contaduria",
        "Cuenta": "/cuenta",
      },

      // Perfil y permisos
      perfil: null,
      permisos: { ...DEFAULT_PERMS },
      loadingPerms: false,

      // Alias de permisos (front) → sin tocar el back
      // 'produccion_proyeccion' usará el mismo flag que 'produccion_agregar_estanque'
      permAliases: {
        produccion_proyeccion: "produccion_agregar_estanque",
      },

      // Base de la API (configurable por .env)
      apiBase: import.meta.env.VITE_API_URL || "/api",
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
    // Menús superiores visibles por permisos
    visibleMenuItems() {
      const allowed = [];
      if (this.can("menu_produccion")) allowed.push("Producción");
      if (this.can("menu_reporte")) allowed.push("Reporte");
      if (this.can("menu_almacen")) allowed.push("Almacén");
      if (this.can("menu_estadistico")) allowed.push("Estadístico");
      if (this.can("menu_contaduria")) allowed.push("Contaduría");
      // "Cuenta" visible siempre
      allowed.push("Cuenta");
      return allowed;
    },
  },
  methods: {
    // === Token helpers ===
    getStoredAccessToken() {
      const keys = ["accessToken", "access", "token", "jwt", "authToken"];
      for (const k of keys) {
        const v = localStorage.getItem(k);
        if (v) return v;
      }
      try {
        const m = document.cookie.match(/(?:^|; )(?:accessToken|access|token|jwt)=([^;]+)/);
        if (m) return decodeURIComponent(m[1]);
      } catch (_e) {}
      return null;
    },
    configurarToken() {
      const token = this.getStoredAccessToken();
      if (!token) {
        delete axios.defaults.headers.common["Authorization"];
        return;
      }
      axios.defaults.headers.common["Authorization"] =
        token.startsWith("Bearer ") ? token : `Bearer ${token}`;
    },

    // === Permisos helpers ===
    can(key) {
      return Boolean(this.permisos && this.permisos[key]);
    },
    has(key) {
      // alias → canon (si existe)
      const canon = this.permAliases?.[key] || key;
      const parent = this.parentFor(canon);
      if (parent && !this.can(parent)) return false;
      return Boolean(this.permisos && this.permisos[canon]);
    },
    parentFor(subKey) {
      if (subKey.startsWith("produccion_")) return "menu_produccion";
      if (subKey.startsWith("reporte_")) return "menu_reporte";
      if (subKey.startsWith("almacen_")) return "menu_almacen";
      if (subKey.startsWith("estadistico_")) return "menu_estadistico";
      if (subKey.startsWith("contaduria_")) return "menu_contaduria";
      return null;
    },

    // === Menús ===
    changeMenu(menuItem) {
      this.currentMenu = menuItem;
      this.isMenuOpen = true;
      if (menuItem !== "Cuenta" && !this.visibleMenuItems.includes(menuItem)) {
        this.ensureValidCurrentMenu();
        return;
      }
      const route = this.menuRouteMap[menuItem];
      if (route && this.$route.path !== route) this.$router.push(route);
    },
    ensureValidCurrentMenu() {
      const firstAllowed = this.visibleMenuItems.find(m => m !== "Cuenta");
      const target = firstAllowed || "Cuenta";
      if (this.currentMenu !== target) {
        this.currentMenu = target;
        const route = this.menuRouteMap[target];
        if (route && this.$route.path !== route) this.$router.push(route);
      }
    },

    // === Navegación/UX ===
    onNavClick() { if (this.isOverlayMode) this.closeMenu(); },
    openMenu() { this.isMenuOpen = true; },
    closeMenu() { this.isMenuOpen = false; },
    toggleMenu() { this.isMenuOpen = !this.isMenuOpen; },
    onResize() {
      this.viewportWidth = window.innerWidth;
      if (!this.isOverlayMode) this.isMenuOpen = true;
    },

    // === API ===
    async fetchPerfilActual() {
      const url = `${this.apiBase}/perfiles/me/`;
      const { data } = await axios.get(url);
      return data;
    },
    async fetchPermisos(_perfil) {
      const url = `${this.apiBase}/permisos/mis-permisos/`;
      const obj = (await axios.get(url)).data;
      const toBool = (v) =>
        v === true || v === 1 || v === "1" || (typeof v === "string" && v.toLowerCase() === "true");
      const cleaned = {};
      for (const k of Object.keys(DEFAULT_PERMS)) cleaned[k] = toBool(obj?.[k]);
      return cleaned;
    },

    // === Boot ===
    async bootstrapPerfilYPermisos() {
      if (!this.loggedIn) return;
      this.loadingPerms = true;
      try {
        const perfil = await this.fetchPerfilActual();
        this.perfil = perfil || null;

        const permisos = await this.fetchPermisos(perfil);
        this.permisos = { ...DEFAULT_PERMS, ...(permisos || {}) };

        this.ensureValidCurrentMenu();
      } catch (err) {
        console.error("Error cargando perfil/permisos:", err);
        this.permisos = { ...DEFAULT_PERMS };
        this.currentMenu = "Cuenta";
        const route = this.menuRouteMap["Cuenta"];
        if (this.$route.path !== route) this.$router.push(route);
      } finally {
        this.loadingPerms = false;
      }
    },

    // === Sesión ===
    onLogin() {
      this.loggedIn = true;
      this.configurarToken();
      this.bootstrapPerfilYPermisos();
    },
    logout() {
      const keys = ["accessToken", "access", "token", "jwt", "authToken"];
      for (const k of keys) localStorage.removeItem(k);
      document.cookie = "accessToken=; Max-Age=0; path=/;";
      document.cookie = "token=; Max-Age=0; path=/;";
      delete axios.defaults.headers.common["Authorization"];
      this.loggedIn = false;
      this.perfil = null;
      this.permisos = { ...DEFAULT_PERMS };
      this.$router.push("/");
    },
  },

  created() {
    this.configurarToken();
    this.isMenuOpen = window.innerWidth >= this.overlayBreakpoint;
    const token = this.getStoredAccessToken();
    if (token) {
      this.loggedIn = true;
      this.bootstrapPerfilYPermisos();
    }
  },
  mounted() { window.addEventListener("resize", this.onResize); },
  beforeUnmount() { window.removeEventListener("resize", this.onResize); },
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
  width: 100%; text-align: left;
  background: transparent; border: none; cursor: pointer; /* para el botón logout */
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
