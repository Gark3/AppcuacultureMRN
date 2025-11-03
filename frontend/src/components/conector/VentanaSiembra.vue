<template>
  <!-- Encabezado + buscador -->
  <section class="card">
    <div class="card__header">
      <h2 class="card__title">Selecciona un Estanque</h2>
      <p class="card__sub">Busca un estanque disponible (sin siembra activa) para iniciar la siembra.</p>
    </div>

    <div class="field">
      <label for="busqueda">Buscar estanque</label>
      <input
        id="busqueda"
        v-model="busqueda"
        class="input"
        type="text"
        placeholder="Nombre, infraestructura, ubicación, etc."
      />
    </div>
  </section>

  <!-- Carrusel -->
  <section class="container container--fluid">
    <div class="carousel">
      <!-- Prev -->
      <button
        v-if="showNav"
        class="nav-btn nav-btn--prev"
        :disabled="!canPrev"
        @click="prev"
        aria-label="Anterior"
      >‹</button>

      <!-- Viewport -->
      <div
        class="viewport"
        ref="viewport"
        :style="{'--slides': slides, '--gap': gap + 'px'}"
        @scroll.passive="onScroll"
      >
        <div
          class="track"
          ref="track"
          :class="{ 'track--center': total <= visible }"
        >
          <article
            v-for="(estanque, i) in estanquesFiltrados"
            :key="getIdEstanque(estanque) ?? i"
            class="card slide"
          >
            <div class="card__header">
              <h3 class="card__title">{{ estanque.nombre || '—' }}</h3>
              <p class="card__sub">
                <strong>Superficie:</strong> {{ estanque.superficie ?? '—' }} m² ·
                <strong>Profundidad:</strong> {{ estanque.profundidad ?? '—' }} m
              </p>
            </div>

            <div class="meta">
              <p><strong>Infraestructura:</strong> {{ estanque.infraestructura || '—' }}</p>
              <p><strong>Ubicación:</strong> {{ estanque.ubicacion || '—' }}</p>
            </div>

            <div class="mt-2">
              <button
                class="btn btn--accent btn--lg slide__btn"
                @click="irAFormularioSiembra(getIdEstanque(estanque))"
                title="Usar este estanque para siembra"
              >
                Utilizar Estanque
              </button>
            </div>
          </article>
        </div>
      </div>

      <!-- Next -->
      <button
        v-if="showNav"
        class="nav-btn nav-btn--next"
        :disabled="!canNext"
        @click="next"
        aria-label="Siguiente"
      >›</button>
    </div>

    <!-- Dots -->
    <div v-if="pages > 1" class="dots">
      <button
        v-for="n in pages"
        :key="n"
        class="dot"
        :class="{ active: currentIndex === (n-1) }"
        @click="goTo(n-1)"
        :aria-label="`Ir al slide ${n}`"
      />
    </div>

    <!-- Mensajes -->
    <p v-if="cargando" class="text-muted mt-3">Cargando estanques…</p>
    <p v-else-if="!estanquesFiltrados.length" class="text-muted mt-3">
      No hay estanques disponibles para siembra.
    </p>
    <p v-else-if="error" class="text-muted mt-3">{{ error }}</p>
  </section>
</template>

<script>
import api from '@/services/axios';

export default {
  name: 'SeleccionarEstanqueSiembra',
  data() {
    return {
      estanques: [],
      busqueda: '',
      cargando: false,
      error: null,
      // Carrusel
      slides: 3,   // 3/2/1 (desktop/tablet/móvil)
      gap: 16,
      currentIndex: 0,
    };
  },
  computed: {
    estanquesFiltrados() {
      const filtro = this.busqueda.trim().toLowerCase();
      if (!filtro) return this.estanques;
      return this.estanques.filter((e) =>
        ['nombre', 'infraestructura', 'forma', 'ubicacion']
          .map((k) => e?.[k])
          .filter(Boolean)
          .some((v) => String(v).toLowerCase().includes(filtro))
      );
    },
    total() { return this.estanquesFiltrados.length; },
    visible() { return this.slides; },
    pages() { return Math.max(1, this.total - this.visible + 1); }, // avanza de 1 en 1
    canPrev() { return this.currentIndex > 0; },
    canNext() { return this.currentIndex < this.pages - 1; },
    showNav() { return this.total > this.visible; },
  },
  methods: {
    // ---------- Normalizadores de ids ----------
    getIdEstanque(obj) {
      // Acepta: {id}, {id_estanque}, {estanque:{id|id_estanque}}, número plano
      const raw =
        obj?.id ??
        obj?.id_estanque ??
        (obj && typeof obj === 'object' && ('estanque' in obj)
          ? (obj.estanque?.id ?? obj.estanque?.id_estanque ?? obj.estanque)
          : null) ??
        obj;
      return raw == null || raw === '' ? null : Number(raw);
    },
    getIdAcuicola(obj) {
      // Acepta: {acuicola_id}, {id_acuicola}, {acuicola:{id}}, número plano
      const raw =
        (obj && typeof obj === 'object'
          ? (obj.acuicola_id ?? obj.id_acuicola ?? obj.id ?? obj.acuicola ?? null)
          : obj);
      return raw == null || raw === '' ? null : Number(raw);
    },

    // ---------- Regla de siembra ACTIVA ----------
    // ACTIVA solo si: estado === 1 y estatus === 0
    isSiembraActiva(s) {
      const estado  = Number(s?.estado ?? 0);
      // estatus puede venir como 0/1 o boolean
      const estatus = (s?.estatus === false) ? 0 : Number(s?.estatus ?? 0);
      return estado === 1 && estatus === 0;
    },

    async obtenerEstanques() {
      this.cargando = true;
      this.error = null;
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) {
          this.estanques = [];
          this.error = 'No hay sesión activa.';
          return;
        }
        const userAcuicolaId = Number(user.acuicola);

        // 1) Traer datos
        const [siembrasResp, estanquesResp] = await Promise.all([
          api.get('/siembra/'),
          api.get('/estanque/'),
        ]);

        const todasSiembras = Array.isArray(siembrasResp.data) ? siembrasResp.data : [];
        const todosEstanques = Array.isArray(estanquesResp.data) ? estanquesResp.data : [];

        // 2) Estanques con siembra ACTIVA (estado=1, estatus=0) en MI acuícola
        const ocupados = new Set(
          todasSiembras
            .filter((s) => {
              const acuicolaSiembra = this.getIdAcuicola(s.acuicola_id ?? s.acuicola);
              return this.isSiembraActiva(s) && acuicolaSiembra === userAcuicolaId;
            })
            .map((s) => this.getIdEstanque(s.estanque ?? s.estanque_id ?? s))
            .filter((id) => id != null)
        );

        // 3) Disponibles = estanques de MI acuícola y NO ocupados
        this.estanques = todosEstanques.filter((e) => {
          const acuicolaId = this.getIdAcuicola(e.acuicola_id ?? e.acuicola);
          if (acuicolaId !== userAcuicolaId) return false;

          // Si tu Estanque tiene "estatus" (activo/inactivo), respétalo; si no, asume true.
          const activo = (typeof e.estatus !== 'undefined') ? !!e.estatus : true;
          if (!activo) return false;

          const idE = this.getIdEstanque(e);
          return idE != null && !ocupados.has(idE);
        });

        // reajusta índice si cambió el total visible
        if (this.currentIndex > this.pages - 1) {
          this.currentIndex = Math.max(0, this.pages - 1);
        }
        this.$nextTick(this.scrollToIndex);
      } catch (error) {
        console.error('Error al obtener estanques:', error);
        this.error = 'No se pudo cargar la lista de estanques.';
        this.estanques = [];
      } finally {
        this.cargando = false;
      }
    },

    irAFormularioSiembra(estanqueId) {
      this.$router.push(`/producción/siembra/registro/${estanqueId}`);
    },

    // ---------- Carrusel ----------
    slideWidth() {
      const track = this.$refs.track;
      if (!track || !track.firstElementChild) return 0;
      const slide = track.firstElementChild;
      const rect = slide.getBoundingClientRect();
      const gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap || '0');
      return rect.width + gap;
    },
    scrollToIndex() {
      const vp = this.$refs.viewport;
      if (!vp) return;
      const x = this.currentIndex * this.slideWidth();
      vp.scrollTo({ left: x, behavior: 'smooth' });
    },
    prev() {
      if (!this.canPrev) return;
      this.currentIndex -= 1;
      this.scrollToIndex();
    },
    next() {
      if (!this.canNext) return;
      this.currentIndex += 1;
      this.scrollToIndex();
    },
    goTo(idx) {
      this.currentIndex = Math.min(Math.max(0, idx), this.pages - 1);
      this.scrollToIndex();
    },
    onScroll() {
      const vp = this.$refs.viewport;
      if (!vp) return;
      const w = this.slideWidth();
      if (w > 0) this.currentIndex = Math.round(vp.scrollLeft / w);
    },
    setSlidesByViewport() {
      const w = window.innerWidth;
      this.slides = w >= 1024 ? 3 : w >= 700 ? 2 : 1;
      this.$nextTick(this.scrollToIndex);
    },
  },

  mounted() {
    this.obtenerEstanques();
    this.setSlidesByViewport();
    window.addEventListener('resize', this.setSlidesByViewport);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.setSlidesByViewport);
  },
};
</script>

<style scoped>
/* contenedor fluido */
.container--fluid { max-width: 1400px; }

/* carrusel */
.carousel {
  position: relative;
  width: 100%;
  margin-top: 10px;
}

.viewport {
  overflow-x: auto;
  overflow-y: hidden;
  width: 100%;
  scroll-behavior: smooth;
}
.viewport::-webkit-scrollbar { height: 8px; }
.viewport::-webkit-scrollbar-thumb { background: transparent; }

.track {
  display: flex;
  gap: var(--gap);
  align-items: stretch;
  scroll-behavior: smooth;
}
.track--center { justify-content: center; }

/* cada slide ocupa 1/N del ancho visible */
.slide {
  flex: 0 0 calc((100% - (var(--gap) * (var(--slides) - 1))) / var(--slides));
  min-width: calc((100% - (var(--gap) * (var(--slides) - 1))) / var(--slides));
}

/* evitar que el botón herede width: 100% */
.slide__btn { width: auto !important; display: inline-flex; }

/* navegación */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: rgba(0,0,0,.35);
  color: #fff;
  width: 36px;
  height: 48px;
  border-radius: 10px;
  cursor: pointer;
  z-index: 5;
}
.nav-btn:hover { background: rgba(0,0,0,.5); }
.nav-btn:disabled { opacity: .4; cursor: default; }
.nav-btn--prev { left: -6px; }
.nav-btn--next { right: -6px; }

/* dots */
.dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 10px;
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: #d1d5db; border: none; cursor: pointer; }
.dot.active { background: #7f1d1d; }

/* contenido */
.meta p { margin: 6px 0; }
</style>
