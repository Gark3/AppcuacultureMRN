<template>
  <!-- Encabezado + buscador -->
  <section class="card">
    <div class="card__header">
      <h2 class="card__title">Siembras Activas</h2>
      <p class="card__sub">Filtra y registra la <strong>calidad del agua</strong> de tus siembras activas.</p>
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
        <div class="track" ref="track" :class="{ 'track--center': total <= visible }">
          <article
            v-for="(s,i) in siembrasFiltradas"
            :key="s.id_siembra || i"
            class="card slide"
          >
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
              <p><strong>Ubicación:</strong> {{ s.estanque_ubicacion || '—' }}</p>
              <p><strong>Fecha de Siembra:</strong> {{ s.fecha || '—' }}</p>
            </div>

            <div class="mt-2">
              <button
                class="btn btn--primary btn--lg slide__btn"
                @click="registrarCalidad(s.id_siembra)"
                title="Registrar calidad del agua"
              >
                Registrar Calidad del Agua
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
  </section>
</template>

<script>
import axios from '@/services/axios';

export default {
  name: 'SiembrasActivasCalidadAgua',
  data() {
    return {
      siembras: [],
      busqueda: '',
      // carrusel
      slides: 3,   // 3/2/1 (desktop/tablet/móvil)
      gap: 16,     // px entre tarjetas
      currentIndex: 0,
    };
  },
  computed: {
    siembrasFiltradas() {
      const f = this.busqueda.trim().toLowerCase();
      if (!f) return this.siembras;
      return this.siembras.filter((s) =>
        Object.values(s).some((v) => String(v ?? '').toLowerCase().includes(f))
      );
    },
    total() { return this.siembrasFiltradas.length; },
    visible() { return this.slides; },
    pages() { return Math.max(1, this.total - this.visible + 1); }, // desplaza 1 por vez
    canPrev() { return this.currentIndex > 0; },
    canNext() { return this.currentIndex < this.pages - 1; },
    showNav() { return this.total > this.visible; },
  },
  methods: {
    async obtenerSiembras() {
      try {
        const user = JSON.parse(localStorage.getItem('user'));

        const [siembrasRes, estanquesRes] = await Promise.all([
          axios.get('/siembra/'),
          axios.get('/estanque/'),
        ]);

        const estanques = estanquesRes.data || [];

        this.siembras = (siembrasRes.data || [])
          .filter((s) => s.estado === 1 && s.acuicola === user.acuicola)
          .map((s) => {
            const e = estanques.find((x) => x.id_estanque === s.estanque) || {};
            return {
              ...s,
              estanque_nombre: e.nombre || '',
              estanque_superficie: e.superficie ?? '',
              estanque_profundidad: e.profundidad ?? '',
              estanque_infraestructura: e.infraestructura || '',
              estanque_ubicacion: e.ubicacion || '',
            };
          });

        // reajusta índice si cambió el total
        if (this.currentIndex > this.pages - 1) {
          this.currentIndex = Math.max(0, this.pages - 1);
        }
        this.$nextTick(this.scrollToIndex);
      } catch (error) {
        console.error('Error al obtener siembras o estanques:', error);
      }
    },

    registrarCalidad(id) {
      this.$router.push(`/producción/calidad-agua/registro/${id}`);
    },

    // --- Carrusel
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
    this.obtenerSiembras();
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

/* evitar que el botón herede width: 100% de estilos globales */
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

/* ajustes móviles */
@media (max-width: 700px) {
  .nav-btn--prev { left: -2px; }
  .nav-btn--next { right: -2px; }
}
</style>
