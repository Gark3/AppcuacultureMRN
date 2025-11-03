<template>
  <!-- Encabezado + buscador -->
  <section class="card">
    <div class="card__header">
      <h2 class="card__title">Siembras Activas</h2>
      <p class="card__sub">
        Filtra y registra la <strong>cosecha</strong> de tus siembras activas.
      </p>
    </div>

    <div class="field">
      <label for="busqueda">Buscar siembra</label>
      <input
        id="busqueda"
        v-model="busqueda"
        class="input"
        type="text"
        placeholder="Nombre, especie, estanque, etapa, etc."
      />
    </div>
  </section>

  <!-- Carrusel con scroll-snap (sin descuadres) -->
  <section
    class="carousel container container--fluid"
    :class="{ 'carousel--compact': totalSlides <= visible }"
  >
    <div class="viewport" ref="viewport">
      <div class="track" :style="{ gap: gap + 'px' }" ref="track">
        <div
          v-for="(s, i) in siembrasFiltradas"
          :key="s.id_siembra || i"
          class="slide"
          :style="slideStyle"
        >
          <article class="card card--fill">
            <div class="card__header">
              <h3 class="card__title">{{ s.estanque_nombre || '—' }}</h3>
              <p class="card__sub">
                <strong>Especie:</strong> {{ s.especie || '—' }} ·
                <strong>Etapa:</strong> {{ s.etapa || '—' }}
              </p>
            </div>

            <div class="meta">
              <p><strong>Superficie:</strong> {{ s.estanque_superficie ?? '—' }} m²</p>
              <p><strong>Profundidad:</strong> {{ s.estanque_profundidad ?? '—' }} m</p>
              <p><strong>Infraestructura:</strong> {{ s.estanque_infraestructura || '—' }}</p>
              <p class="ellipsis"><strong>Ubicación:</strong> {{ s.estanque_ubicacion || '—' }}</p>
              <p><strong>Fecha de Siembra:</strong> {{ s.fecha || '—' }}</p>
            </div>

            <div class="mt-auto">
              <button
                class="btn btn--accent btn--lg w-100"
                @click="registrarCosecha(s.id_siembra)"
              >
                Registrar Cosecha
              </button>
            </div>
          </article>
        </div>
      </div>

      <!-- Flechas -->
      <button
        v-if="totalSlides > visible"
        class="nav-btn nav-btn--prev"
        type="button"
        :disabled="!canPrev"
        @click="prev"
        aria-label="Anterior"
      >‹</button>

      <button
        v-if="totalSlides > visible"
        class="nav-btn nav-btn--next"
        type="button"
        :disabled="!canNext"
        @click="next"
        aria-label="Siguiente"
      >›</button>
    </div>

    <!-- Dots -->
    <div v-if="totalSlides > visible" class="dots">
      <button
        v-for="(pg, idx) in pageCount"
        :key="idx"
        type="button"
        class="dot"
        :class="{ active: pageIndex === idx }"
        @click="goToPage(idx)"
        :aria-label="`Ir a grupo ${idx + 1}`"
      />
    </div>
  </section>
</template>

<script>
import axios from '@/services/axios';

export default {
  name: 'SiembrasActivasCosecha',
  data() {
    return {
      siembras: [],
      busqueda: '',

      // Carrusel
      vw: typeof window !== 'undefined' ? window.innerWidth : 1280,
      gap: 16,               // espacio entre tarjetas (px)
      perViewDesktop: 3,     // >=1024px
      perViewTablet: 2,      // 640–1023px
      perViewMobile: 1,      // <640px

      // Estado de scroll
      index: 0,              // índice “lógico” (tarjeta inicial visible)
      stepPx: 0              // ancho de una tarjeta + gap (px)
    };
  },
  computed: {
    siembrasFiltradas() {
      const filtro = this.busqueda.trim().toLowerCase();
      if (!filtro) return this.siembras;
      return this.siembras.filter((s) =>
        Object.values(s).some((v) => String(v ?? '').toLowerCase().includes(filtro))
      );
    },

    totalSlides() { return this.siembrasFiltradas?.length || 0; },
    visible() {
      if (this.vw < 640) return this.perViewMobile;
      if (this.vw < 1024) return this.perViewTablet;
      return this.perViewDesktop;
    },
    maxIndex() { return Math.max(0, this.totalSlides - this.visible); },
    canPrev() { return this.index > 0; },
    canNext() { return this.index < this.maxIndex; },
    pageIndex() { return Math.floor(this.index); },
    pageCount() { return Math.max(1, this.totalSlides - this.visible + 1); },

    // Ancho flexible para cada slide, sin descuadres, ocupando todo el contenedor
    slideStyle() {
      const v = Math.max(1, Math.min(this.visible, this.totalSlides || 1));
      return {
        flex: `0 0 calc((100% - ${this.gap * (v - 1)}px) / ${v})`,
        maxWidth: `calc((100% - ${this.gap * (v - 1)}px) / ${v})`
      };
    },
  },
  methods: {
    async obtenerSiembras() {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const [siembrasRes, estanquesRes] = await Promise.all([
          axios.get('/siembra/'),
          axios.get('/estanque/')
        ]);
        const estanques = estanquesRes.data || [];
        this.siembras = (siembrasRes.data || [])
          .filter(s => s.estado === 1 && s.acuicola === user.acuicola)
          .map(s => {
            const e = estanques.find(x => x.id_estanque === s.estanque) || {};
            return {
              ...s,
              estanque_nombre: e.nombre || '',
              estanque_superficie: e.superficie ?? '',
              estanque_profundidad: e.profundidad ?? '',
              estanque_infraestructura: e.infraestructura || '',
              estanque_ubicacion: e.ubicacion || ''
            };
          });

        this.$nextTick(() => this.measureStep());
      } catch (error) {
        console.error('Error al obtener siembras o estanques:', error);
      }
    },

    // Medir exactamente el “paso”: ancho de una tarjeta + gap
    measureStep() {
      const track = this.$refs.track;
      const slide = track?.querySelector('.slide');
      if (!slide) { this.stepPx = 0; return; }
      const rect = slide.getBoundingClientRect();
      this.stepPx = rect.width + this.gap;
      // Ajustar índice por si cambió el visible
      if (this.index > this.maxIndex) this.index = this.maxIndex;
      this.syncScrollToIndex(false);
    },

    // Sincroniza el scroll horizontal al índice actual
    syncScrollToIndex(smooth = true) {
      const vp = this.$refs.viewport;
      if (!vp || !this.stepPx) return;
      const left = this.index * this.stepPx;
      vp.scrollTo({ left, behavior: smooth ? 'smooth' : 'auto' });
    },

    // Derivar índice según el scroll actual (para dots y estado de flechas)
    deriveIndexFromScroll() {
      const vp = this.$refs.viewport;
      if (!vp || !this.stepPx) return;
      const idx = Math.round(vp.scrollLeft / this.stepPx);
      this.index = Math.max(0, Math.min(idx, this.maxIndex));
    },

    prev() {
      if (!this.canPrev) return;
      this.index -= 1;
      this.syncScrollToIndex(true);
    },
    next() {
      if (!this.canNext) return;
      this.index += 1;
      this.syncScrollToIndex(true);
    },
    goToPage(p) {
      this.index = Math.max(0, Math.min(p, this.maxIndex));
      this.syncScrollToIndex(true);
    },

    registrarCosecha(id) {
      this.$router.push(`/producción/cosecha/registro/${id}`);
    },

    onResize() {
      this.vw = window.innerWidth;
      this.$nextTick(() => this.measureStep());
    }
  },
  mounted() {
    this.obtenerSiembras();
    this.onResize();
    window.addEventListener('resize', this.onResize, { passive: true });

    // Vincular scroll para actualizar índice y evitar desalineación
    const vp = this.$refs.viewport;
    if (vp) vp.addEventListener('scroll', this.deriveIndexFromScroll, { passive: true });
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.onResize);
    const vp = this.$refs.viewport;
    if (vp) vp.removeEventListener('scroll', this.deriveIndexFromScroll);
  }
};
</script>

<style scoped>
/* Que el carrusel pueda ocupar el 100% horizontal */
.container.container--fluid { max-width: 100% !important; }

/* Estructura del carrusel */
.carousel { margin-top: 12px; }
.viewport {
  position: relative;
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  border-radius: var(--radius-lg, 14px);
  background: var(--color-surface, #fff);
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,.10));
  scroll-behavior: smooth;
  scrollbar-width: none;        /* Firefox */
}
.viewport::-webkit-scrollbar { display: none; } /* Chrome/Safari */

/* Pista y slides */
.track {
  display: flex;
  width: max-content;
  padding: 20px;
  box-sizing: border-box;
  scroll-snap-type: x mandatory;
}
.slide {
  display: flex;
  scroll-snap-align: start;
}

/* Tarjeta */
.card--fill { display: flex; flex-direction: column; height: 100%; width: 100%; }
.meta p { margin: 6px 0; font-size: .95rem; }
.ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mt-auto { margin-top: auto; }
.w-100 { width: 100%; }

/* Flechas */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  width: 40px; height: 40px;
  border-radius: 999px;
  background: rgba(0,0,0,.35);
  color: #fff; font-size: 22px;
  display: grid; place-items: center;
  cursor: pointer;
}
.nav-btn--prev { left: 10px; }
.nav-btn--next { right: 10px; }
.nav-btn:disabled { opacity: .35; cursor: default; }

/* Dots */
.dots {
  display: flex; justify-content: center; gap: 10px;
  padding: 10px 0 14px;
}
.dot {
  width: 9px; height: 9px; border-radius: 999px;
  background: #c7c7c7; border: none; cursor: pointer;
}
.dot.active { background: #8d2a2a; }

/* Si hay 1–2 tarjetas: centramos y ocultamos flechas/dots vía lógica de plantilla */
.carousel--compact .track { justify-content: center; }

/* Responsive */
@media (max-width: 640px) {
  .track { padding: 14px; }
  .nav-btn { width: 36px; height: 36px; font-size: 20px; }
}
</style>
