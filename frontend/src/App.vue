<template>
  <div class="theme-ipn">
    <div v-if="isAuthRoute">
      <router-view />
    </div>

    <div v-else-if="loggedIn" class="app-shell">
      <!-- TOPBAR -->
      <header class="topbar login-like" @keydown.esc="closeTopGrid">
        <div class="brand-group">
          <button
            class="hamburger"
            @click="toggleMenu"
            aria-label="Abrir/cerrar menú"
            :aria-expanded="isMenuOpen"
            aria-controls="asideMenu"
            title="Menú"
          >☰</button>

          <div class="brand" @click="changeMenu(currentMenu || 'Producción')" role="button" tabindex="0">
            <img class="brand-logo" src="@/assets/AppQuacultureLogo.png" alt="AppQuaculture" draggable="false" />
            <span class="brand-name">AppQuaculture</span>
          </div>
        </div>

        <!-- NAV superior; “fantasma” solo cuando hay wrap. Reservamos UNA FILA -->
        <nav
          ref="topNav"
          class="main-nav"
          aria-label="Navegación principal"
          :class="{ 'ghost-when-wrapped': isTopWrapped }"
          :style="isTopWrapped ? { height: rowH + 'px' } : { height: '' }"
        >
          <button
            v-for="item in visibleMenuItems"
            :key="item"
            :class="['nav-pill', { active: currentMenu === item }]"
            @click="onTopItemClick(item)"
            :title="`Ir a ${item}`"
          >
            <span class="pill-ico" aria-hidden="true">{{ icons[item] || '•' }}</span>
            <span class="pill-text">{{ item }}</span>
          </button>
        </nav>

        <!-- Botón GRID (solo cuando hay wrap) -->
        <button
          v-if="isTopWrapped"
          class="top-grid-btn"
          @click="openTopGrid"
          aria-haspopup="dialog"
          :aria-expanded="isTopGridOpen"
          aria-controls="topGridSheet"
          title="Abrir opciones"
        >
          ⬛⬛
        </button>
      </header>

      <!-- Sheet superior con opciones en rejilla -->
      <transition name="fade">
        <div
          v-if="isTopGridOpen"
          class="topgrid-backdrop"
          @click.self="closeTopGrid"
        >
          <section
            id="topGridSheet"
            class="topgrid-sheet"
            role="dialog"
            aria-modal="true"
            aria-label="Menú superior"
            ref="topGridSheet"
            tabindex="-1"
          >
            <header class="topgrid-header">
              <span class="topgrid-title">Menú</span>
              <button class="topgrid-close" @click="closeTopGrid" aria-label="Cerrar">✕</button>
            </header>

            <div class="topgrid-grid">
              <button
                v-for="item in visibleMenuItems"
                :key="`grid-${item}`"
                class="topgrid-tile"
                @click="onGridGo(item)"
              >
                <span class="tile-ico">{{ icons[item] || '•' }}</span>
                <span class="tile-text">{{ item }}</span>
              </button>
            </div>
          </section>
        </div>
      </transition>

      <div class="main-container">
        <!-- ASIDE -->
        <aside
          id="asideMenu"
          class="side-menu sheet"
          :class="{ 'open': isMenuOpen }"
          aria-label="Submenú de sección"
        >
          <div class="side-header">
            <span class="side-title">{{ currentMenu || 'Menú' }}</span>
            <button class="side-close" @click="closeMenu" aria-label="Cerrar menú">✕</button>
          </div>

          <ul class="side-list" v-if="!loadingPerms">
            <!-- Producción -->
            <template v-if="currentMenu === 'Producción' && can('menu_produccion')">
              <li class="side-group">Operación</li>
              <li v-if="has('produccion_agregar_estanque')">
                <router-link to="/producción/agregar-estanque" class="side-link" @click="onNavClick">Agregar estanque</router-link>
              </li>
              <li v-if="has('produccion_siembra')">
                <router-link to="/producción/siembra" class="side-link" @click="onNavClick">Siembra</router-link>
              </li>
              <li v-if="has('produccion_alimentar')">
                <router-link to="/producción/alimentar" class="side-link" @click="onNavClick">Alimentar</router-link>
              </li>
              <li v-if="has('produccion_calidad_agua')">
                <router-link to="/producción/calidad-agua" class="side-link" @click="onNavClick">Calidad de agua</router-link>
              </li>
              <li v-if="has('produccion_dieta')">
                <router-link to="/producción/dieta" class="side-link" @click="onNavClick">Dieta</router-link>
              </li>
              <li v-if="has('produccion_crecimiento')">
                <router-link to="/producción/crecimiento" class="side-link" @click="onNavClick">Crecimiento</router-link>
              </li>
              <li class="side-sep"></li>
              <li class="side-group">Cierre</li>
              <li v-if="has('produccion_cosecha')">
                <router-link to="/producción/cosecha" class="side-link" @click="onNavClick">Cosecha</router-link>
              </li>
              <li v-if="has('produccion_tratamientos')">
                <router-link to="/producción/tratamientos" class="side-link" @click="onNavClick">Tratamientos</router-link>
              </li>
              <li v-if="has('produccion_cuarentena')">
                <router-link to="/producción/cuarentena" class="side-link" @click="onNavClick">Proyeccion de Siembra</router-link>
              </li>
            </template>

            <!-- Reporte -->
            <template v-else-if="currentMenu === 'Reporte' && can('menu_reporte')">
              <li class="side-group">Reportes</li>
              <li v-if="has('reporte_estanque')">
                <router-link to="/reporte/estanque" class="side-link" @click="onNavClick">Estanque</router-link>
              </li>
              <li v-if="has('reporte_crecimiento')">
                <router-link to="/reporte/crecimiento" class="side-link" @click="onNavClick">Crecimiento</router-link>
              </li>
              <li v-if="has('reporte_gpc')">
                <router-link to="/reporte/gpc" class="side-link" @click="onNavClick">GPC</router-link>
              </li>
              <li v-if="has('reporte_calidad_agua')">
                <router-link to="/reporte/calidad-agua" class="side-link" @click="onNavClick">Calidad de agua</router-link>
              </li>
            </template>

            <!-- Almacén -->
            <template v-else-if="currentMenu === 'Almacén' && can('menu_almacen')">
              <li class="side-group">Inventarios</li>
              <li v-if="has('almacen_inventario')">
                <router-link to="/almacén/inventario" class="side-link" @click="onNavClick">Inventario</router-link>
              </li>
              <li v-if="has('almacen_inventario_fisico')">
                <router-link to="/almacén/inventario-fisico" class="side-link" @click="onNavClick">Inventario físico</router-link>
              </li>
              <li class="side-sep"></li>
              <li class="side-group">Entradas/Salidas</li>
              <li v-if="has('almacen_entradas')">
                <router-link to="/almacén/entradas" class="side-link" @click="onNavClick">Entradas</router-link>
              </li>
              <li v-if="has('almacen_salidas')">
                <router-link to="/almacén/salidas" class="side-link" @click="onNavClick">Salidas</router-link>
              </li>
              <li class="side-sep"></li>
              <li class="side-group">Catálogos</li>
              <li v-if="has('almacen_proveedores')">
                <router-link to="/almacén/proveedores" class="side-link" @click="onNavClick">Proveedores</router-link>
              </li>
              <li v-if="has('almacen_alta_material')">
                <router-link to="/almacén/alta-material" class="side-link" @click="onNavClick">Alta de material</router-link>
              </li>
              <li v-if="has('almacen_alta_proveedores')">
                <router-link to="/almacén/alta-proveedores" class="side-link" @click="onNavClick">Alta de proveedores</router-link>
              </li>
            </template>

            <!-- Estadístico -->
            <template v-else-if="currentMenu === 'Estadístico' && can('menu_estadistico')">
              <li class="side-group">Pruebas</li>
              <li v-if="has('estadistico_kolmogorov_smirnov')">
                <router-link to="/estadístico/kolmogorov-smirnov" class="side-link" @click="onNavClick">Kolmogorov–Smirnov</router-link>
              </li>
              <li v-if="has('estadistico_shapiro_wilk')">
                <router-link to="/estadístico/shapiro-wilk" class="side-link" @click="onNavClick">Shapiro–Wilk</router-link>
              </li>
              <li v-if="has('estadistico_anova')">
                <router-link to="/estadístico/anova" class="side-link" @click="onNavClick">ANOVA</router-link>
              </li>
            </template>

            <!-- Contaduría -->
            <template v-else-if="currentMenu === 'Contaduría' && can('menu_contaduria')">
              <li class="side-group">Gastos y pagos</li>
              <li v-if="has('contaduria_pagos_servicios')">
                <router-link to="/contaduría/pagos-servicios" class="side-link" @click="onNavClick">Pagos de servicios</router-link>
              </li>
              <li v-if="has('contaduria_mantenimiento')">
                <router-link to="/contaduría/mantenimiento" class="side-link" @click="onNavClick">Mantenimiento</router-link>
              </li>
              <li v-if="has('contaduria_costos_operativos')">
                <router-link to="/contaduría/costos-operativos" class="side-link" @click="onNavClick">Costos operativos</router-link>
              </li>
              <li class="side-sep"></li>
              <li class="side-group">Personal y compras</li>
              <li v-if="has('contaduria_nomina')">
                <router-link to="/contaduría/nomina" class="side-link" @click="onNavClick">Nómina</router-link>
              </li>
              <li v-if="has('contaduria_sueldos')">
                <router-link to="/contaduría/sueldos" class="side-link" @click="onNavClick">Salarios</router-link>
              </li>
              <li v-if="has('contaduria_compras')">
                <router-link to="/contaduría/compras" class="side-link" @click="onNavClick">Compras</router-link>
              </li>
              <li v-if="has('contaduria_ventas')">
                <router-link to="/contaduría/ventas" class="side-link" @click="onNavClick">Ventas</router-link>
              </li>
            </template>

            <!-- Cuenta -->
            <template v-else-if="currentMenu === 'Cuenta'">
              <li class="side-group">Cuenta</li>
              <li>
                <button class="side-link btn-logout" @click="logout">Cerrar sesión</button>
              </li>
            </template>

            <template v-else>
              <li class="side-empty">Selecciona una sección arriba</li>
            </template>
          </ul>

          <ul class="side-list" v-else>
            <li class="side-empty">Cargando permisos…</li>
          </ul>
        </aside>

        <!-- Overlay móvil -->
        <div v-if="isOverlayMode && isMenuOpen" class="overlay" @click="closeMenu"></div>

        <!-- Contenido -->
        <main class="content content--sheet" :class="{ 'with-aside': !isOverlayMode && isMenuOpen }">
          <router-view />
        </main>
      </div>
    </div>

    <div v-else>
      <Login @login="onLogin" />
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Login from "@/components/LoginPage.vue";

const DEFAULT_PERMS = {
  menu_produccion: false,
  menu_reporte: false,
  menu_almacen: false,
  menu_estadistico: false,
  menu_contaduria: false,
  produccion_agregar_estanque: false,
  produccion_siembra: false,
  produccion_alimentar: false,
  produccion_calidad_agua: false,
  produccion_dieta: false,
  produccion_crecimiento: false,
  produccion_cosecha: false,
  produccion_tratamientos: false,
  produccion_cuarentena: false,
  reporte_estanque: false,
  reporte_crecimiento: false,
  reporte_gpc: false,
  reporte_calidad_agua: false,
  almacen_inventario: false,
  almacen_proveedores: false,
  almacen_alta_material: false,
  almacen_alta_proveedores: false,
  almacen_entradas: false,
  almacen_salidas: false,
  almacen_inventario_fisico: false,
  estadistico_kolmogorov_smirnov: false,
  estadistico_shapiro_wilk: false,
  estadistico_anova: false,
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
      isMenuOpen: false,               // << comienza CERRADO en todas las resoluciones
      viewportWidth: window.innerWidth,
      overlayBreakpoint: 1024,
      menuRouteMap: {
        "Producción": "/produccion",
        "Reporte": "/reporte",
        "Almacén": "/almacen",
        "Estadístico": "/estadistico",
        "Contaduría": "/contaduria",
        "Cuenta": "/cuenta",
      },

      perfil: null,
      permisos: { ...DEFAULT_PERMS },
      loadingPerms: false,

      permAliases: { produccion_proyeccion: "produccion_agregar_estanque" },

      apiBase: import.meta.env.VITE_API_URL || "/api",

      icons: {
        "Producción": "🧪",
        "Reporte": "📄",
        "Almacén": "📦",
        "Estadístico": "📊",
        "Contaduría": "💰",
        "Cuenta": "👤",
      },

      // Estado top grid / anti-flicker
      isTopWrapped: false,
      isTopGridOpen: false,
      ro: null,
      rowH: 0,                // altura de UNA fila de pills
      _wrapTimer: null,
    };
  },
  computed: {
    isAuthRoute() {
      const path = this.$route.path;
      return path === "/login" || path === "/registrarusuario";
    },
    isOverlayMode() {
      return this.viewportWidth < this.overlayBreakpoint;
    },
    visibleMenuItems() {
      const allowed = [];
      if (this.can("menu_produccion")) allowed.push("Producción");
      if (this.can("menu_reporte")) allowed.push("Reporte");
      if (this.can("menu_almacen")) allowed.push("Almacén");
      if (this.can("menu_estadistico")) allowed.push("Estadístico");
      if (this.can("menu_contaduria")) allowed.push("Contaduría");
      allowed.push("Cuenta");
      return allowed;
    },
  },
  methods: {
    // token
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

    // permisos
    can(key) { return Boolean(this.permisos && this.permisos[key]); },
    has(key) {
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

    // navegación superior
    onTopItemClick(item) {
      this.changeMenu(item);
      // En móvil abrimos aside para mostrar submenú; en desktop NO auto-abrimos
      if (this.isOverlayMode) this.openMenu();
    },
    changeMenu(menuItem) {
      this.currentMenu = menuItem;
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

    // aside
    onNavClick() { if (this.isOverlayMode) this.closeMenu(); },
    openMenu() { this.isMenuOpen = true; },
    closeMenu() { this.isMenuOpen = false; },
    toggleMenu() { this.isMenuOpen = !this.isMenuOpen; },

    // wrap detector (1 fila) con throttle
    checkTopWrap() {
      if (this._wrapTimer) return;
      this._wrapTimer = setTimeout(() => {
        const el = this.$refs.topNav;
        if (!el) { this.isTopWrapped = false; this.rowH = 0; this._wrapTimer = null; return; }

        const pills = el.querySelectorAll('.nav-pill');
        if (!pills.length) { this.isTopWrapped = false; this.rowH = 0; this._wrapTimer = null; return; }

        // Calcula si hay wrap y la altura de UNA sola fila
        let firstTop = null, wrapped = false, maxH = 0;
        for (const btn of pills) {
          const t = btn.offsetTop;
          const h = btn.offsetHeight || 0;
          if (h > maxH) maxH = h;
          if (firstTop === null) firstTop = t;
          if (t > firstTop + 1) { wrapped = true; }
        }
        this.isTopWrapped = wrapped;
        this.rowH = wrapped ? maxH : 0;

        this._wrapTimer = null;
      }, 80);
    },

    // grid sheet
    openTopGrid() {
      this.isTopGridOpen = true;
      this.$nextTick(() => {
        const sheet = this.$refs.topGridSheet;
        if (sheet && typeof sheet.focus === 'function') sheet.focus();
      });
    },
    closeTopGrid() { this.isTopGridOpen = false; },
    onGridGo(item) { this.changeMenu(item); this.closeTopGrid(); if (this.isOverlayMode) this.openMenu(); },

    onResize() {
      const prevOverlay = this.isOverlayMode;
      this.viewportWidth = window.innerWidth;
      // Solo auto-abrir cuando pasas de móvil -> desktop
      if (prevOverlay && !this.isOverlayMode) this.isMenuOpen = false; // incluso en desktop mantenlo cerrado hasta que el usuario lo abra
      this.checkTopWrap();
    },

    // API
    async fetchPerfilActual() {
      const url = `${this.apiBase}/perfiles/me/`;
      const { data } = await axios.get(url);
      return data;
    },
    async fetchPermisos(_perfil) {
      const url = `${this.apiBase}/permisos/mis-permisos/`;
      const obj = (await axios.get(url)).data;
      const toBool = (v) => v === true || v === 1 || v === "1" || (typeof v === "string" && v.toLowerCase() === "true");
      const cleaned = {};
      for (const k of Object.keys(DEFAULT_PERMS)) cleaned[k] = toBool(obj?.[k]);
      return cleaned;
    },

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
        this.$nextTick(() => this.checkTopWrap());
      }
    },

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
    const token = this.getStoredAccessToken();
    if (token) {
      this.loggedIn = true;
      this.bootstrapPerfilYPermisos();
    }
  },
  mounted() {
    window.addEventListener("resize", this.onResize);
    this.ro = new ResizeObserver(() => this.checkTopWrap());
    this.$nextTick(() => {
      const header = this.$el.querySelector('.topbar.login-like');
      if (header) this.ro.observe(header);
      // Arranca con aside CERRADO (el usuario decide)
      this.isMenuOpen = false;
      this.checkTopWrap();
    });
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.onResize);
    if (this.ro) this.ro.disconnect();
    if (this._wrapTimer) { clearTimeout(this._wrapTimer); this._wrapTimer = null; }
  },
};
</script>

<style scoped>
/* ===== TOPBAR ===== */
.topbar.login-like{
  position: sticky; top: 0; z-index: 10;
  backdrop-filter: blur(8px);
  background: rgba(255,255,255,.75);
  border-bottom: 1px solid rgba(0,0,0,.06);
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 10px clamp(12px, 4vw, 28px);
}
.brand-group{ display:flex; align-items:center; gap:8px; }
.hamburger{
  border:0; background:transparent; cursor:pointer;
  font-size:20px; padding:8px 10px; border-radius:10px; color:#583a34;
}
.hamburger:hover{ background:rgba(141,42,42,.08); }
.brand{ display:flex; align-items:center; gap:10px; user-select:none; cursor:pointer; }
.brand:focus{ outline:2px solid #8d2a2a33; outline-offset:4px; }
.brand-logo{ height:34px; width:auto; filter:drop-shadow(0 1px 3px rgba(0,0,0,.15)); }
.brand-name{ font-weight:800; letter-spacing:.2px; color:var(--color-primary); }

/* Pills */
.main-nav{ display:flex; gap:clamp(6px,2vw,12px); flex-wrap:wrap; }
.nav-pill{
  border:0; background:transparent; cursor:pointer;
  font-weight:800; padding:8px 14px; border-radius:999px;
  display:flex; align-items:center; gap:8px;
  color:#583a34;
  transition:transform .08s ease, background .2s ease, color .2s ease, box-shadow .2s ease;
}
.nav-pill:hover{ background:rgba(141,42,42,.08); color:var(--color-primary); }
.nav-pill.active{
  background:#ffc107; color:#1f2937;
  box-shadow:0 6px 16px rgba(0,0,0,.08);
}
.pill-ico{ font-size:16px; line-height:1; }

/* Fantasma sin reflow, reservando solo 1 fila (rowH) */
.ghost-when-wrapped{
  visibility: hidden;
  pointer-events: none;
}

/* Botón GRID compacto y estable */
.top-grid-btn{
  border:0; background:rgba(141,42,42,.12); cursor:pointer;
  width: 40px; height: 40px; padding:0; border-radius:10px;
  color:#583a34; display:flex; align-items:center; justify-content:center;
  line-height:1; overflow:hidden; flex: 0 0 40px;
}
.top-grid-btn:hover{ background:rgba(141,42,42,.2); }

/* ===== ASIDE ===== */
.side-menu.sheet{
  position: fixed; top: 70px; left: 12px; bottom: 12px;
  width: 280px; background: rgba(255,255,255,.96); color: var(--color-text);
  transform: translateX(-120%); transition: transform .25s ease;
  z-index: 12; overflow-y: auto;
  border:1px solid var(--color-border); border-radius: 14px;
  box-shadow: 0 12px 28px rgba(0,0,0,.14);
}
.side-menu.open{ transform: translateX(0); }
@media (min-width:1024px){
  .side-menu.sheet{ left:16px; top: 86px; }
}

.side-header{
  display:flex; align-items:center; justify-content:space-between;
  padding:12px 14px; position: sticky; top:0;
  background: rgba(255,255,255,.98);
  border-bottom:1px solid var(--color-border);
  border-top-left-radius:14px; border-top-right-radius:14px;
}
.side-title{ font-weight:900; color:var(--color-primary); }
.side-close{
  background:transparent; color:#6b7280; border:none; cursor:pointer;
  font-size:18px; border-radius:8px; padding:6px 8px;
}
.side-close:hover{ background:rgba(31,41,55,.06); }

.side-list{ list-style:none; padding:10px; margin:0; }
.side-group{
  margin:8px 6px 6px; font-size:12px; text-transform:uppercase;
  letter-spacing:.08em; color:#6b7280; font-weight:800;
}
.side-sep{ height:8px; }
.side-link{
  display:block; width:100%; text-align:left;
  padding:10px 12px; border-radius:10px; text-decoration:none;
  color:var(--color-text); background:transparent; border:none; cursor:pointer;
  transition: background .2s ease, color .2s ease, padding-left .12s ease;
}
.side-link:hover{ background:rgba(141,42,42,.08); color:var(--color-primary); }
.side-link.router-link-active,
.side-link.router-link-exact-active{
  background: rgba(141,42,42,.12);
  color: var(--color-primary);
  box-shadow: inset 0 0 0 1px rgba(141,42,42,.25);
  font-weight:800;
}

/* Overlay móvil */
.overlay{ position:fixed; inset:0; background:rgba(0,0,0,.35); z-index:11; }

/* Contenido */
.content.content--sheet{
  background: var(--color-surface);
  padding: 24px; border-top-left-radius: 14px;
  min-height: calc(100vh - 70px); transition: padding-left .25s ease;
}
@media (min-width:1024px){ .content.with-aside{ padding-left: 320px; } }
@media (max-width:1023.98px){ .content.with-aside{ padding-left: 0; } }

/* ===== Sheet superior (grid) ===== */
.topgrid-backdrop{
  position: fixed; inset: 0; z-index: 40;
  background: rgba(0,0,0,.35);
  display:flex; justify-content:center; align-items:flex-start;
  padding: 12px;
}
.topgrid-sheet{
  outline: none; position: relative; margin-top: 8px;
  width: 100%; max-width: 560px;
  background: rgba(255,255,255,.98);
  border:1px solid var(--color-border); border-radius: 16px;
  box-shadow: 0 16px 40px rgba(0,0,0,.2);
  max-height: 80vh; overflow: hidden; display:flex; flex-direction:column;
}
@media (min-width: 640px){ .topgrid-sheet{ max-width: 720px; } }
.topgrid-header{
  display:flex; align-items:center; justify-content:space-between;
  padding: 12px 14px; border-bottom:1px solid var(--color-border);
  background: rgba(255,255,255,.98);
}
.topgrid-title{ font-weight:900; color:var(--color-primary); }
.topgrid-close{
  background:transparent; border:0; cursor:pointer; color:#6b7280;
  font-size:18px; border-radius:8px; padding:6px 8px;
}
.topgrid-close:hover{ background:rgba(31,41,55,.06); }

/* Rejilla */
.topgrid-grid{
  padding: 14px; display:grid; gap:12px;
  grid-template-columns: repeat(2, minmax(0,1fr));
}
@media (min-width:480px){ .topgrid-grid{ grid-template-columns: repeat(3, minmax(0,1fr)); } }
.topgrid-tile{
  display:flex; align-items:center; gap:12px;
  padding:12px; border-radius:12px; border:1px solid rgba(0,0,0,.06);
  background: #fff; cursor:pointer; text-align:left;
  transition: transform .06s ease, box-shadow .2s ease, background .2s ease;
}
.topgrid-tile:hover{
  background: rgba(141,42,42,.06);
  box-shadow: 0 6px 16px rgba(0,0,0,.08);
}
.tile-ico{ font-size:20px; }
.tile-text{ font-weight:800; color:#583a34; }

/* Fade */
.fade-enter-active, .fade-leave-active{ transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to{ opacity: 0; }

/* Composición / fallback blur */
.side-menu.sheet, .topgrid-sheet, .topbar.login-like { will-change: transform, opacity; transform: translateZ(0); }
@supports not ((backdrop-filter: blur(8px))) { .topbar.login-like{ background: rgba(255,255,255,.92); } }
@media (max-width: 420px){ .topbar.login-like{ backdrop-filter: none; -webkit-backdrop-filter: none; } }

/* Tema oscuro */
:deep(html.theme-dark) .topbar.login-like{ background: rgba(15, 23, 42, 0.6); border-bottom: 1px solid rgba(255,255,255,.08); }
:deep(html.theme-dark) .nav-pill{ color:#e5e7eb; }
:deep(html.theme-dark) .nav-pill:hover{ background: rgba(141,42,42,.22); color:#fff; }
:deep(html.theme-dark) .side-menu.sheet{ background: rgba(15,23,42,.96); color:#e5e7eb; border-color:#273449; }
:deep(html.theme-dark) .side-header{ background: rgba(15,23,42,.98); border-color:#273449; }
:deep(html.theme-dark) .side-link:hover{ background: rgba(141,42,42,.22); color:#fff; }
:deep(html.theme-dark) .side-link.router-link-active{ background: rgba(141,42,42,.28); }

:deep(html.theme-dark) .topgrid-sheet{ background: rgba(15,23,42,.98); border-color:#273449; }
:deep(html.theme-dark) .topgrid-header{ background: rgba(15,23,42,.98); border-color:#273449; }
:deep(html.theme-dark) .topgrid-tile{ background:#0b1220; border-color:#273449; color:#e5e7eb; }
:deep(html.theme-dark) .topgrid-tile:hover{ background: #111a2e; }
</style>
