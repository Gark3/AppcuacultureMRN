<template>
  <section class="card">
    <!-- Encabezado + buscador -->
    <div class="card__header">
      <h2 class="card__title">Siembras Activas</h2>
      <p class="card__sub">Filtra y registra la <strong>cosecha</strong> de tus siembras activas.</p>
    </div>

    <div class="field">
      <label for="busqueda">Buscar siembra</label>
      <input
        id="busqueda"
        v-model="busqueda"
        class="input"
        type="text"
        placeholder="Nombre, especie, estanque, etapa, etc."
        @input="goToStart" 
      />
    </div>
  </section>

  <!-- Carrusel -->
  <section class="carousel container" ref="carouselEl" @keydown.left.prevent="prev" @keydown.right.prevent="next" tabindex="0" aria-label="Carrusel de siembras">
    <!-- Botón previo -->
    <button
      class="nav-btn nav-btn--prev"
      type="button"
      :disabled="!canPrev"
      @click="prev"
      aria-label="Anterior"
      title="Anterior"
    >
      ‹
    </button>

    <!-- Ventana -->
    <div class="viewport">
      <div
        class="track"
        :style="trackStyle"
        role="list"
        aria-live="polite"
      >
        <article
          v-for="siembra in siembrasFiltradas"
          :key="siembra.id_siembra"
          class="card slide"
          :style="slideStyle"
          role="listitem"
        >
          <div class="card__header">
            <h3 class="card__title">{{ siembra.estanque_nombre || '—' }}</h3>
            <p class="card__sub">
              <strong>Especie:</strong> {{ siembra.especie || '—' }} ·
              <strong>Etapa:</strong> {{ siembra.etapa || '—' }}
            </p>
          </div>

          <div class="meta">
            <p><strong>Superficie:</strong> {{ siembra.estanque_superficie ?? '—' }} m²</p>
            <p><strong>Profundidad:</strong> {{ siembra.estanque_profundidad ?? '—' }} m</p>
            <p><strong>Infraestructura:</strong> {{ siembra.estanque_infraestructura || '—' }}</p>
            <p><strong>Ubicación:</strong> {{ siembra.estanque_ubicacion || '—' }}</p>
            <p><strong>Fecha de Siembra:</strong> {{ siembra.fecha || '—' }}</p>
          </div>

          <div class="mt-3">
            <button
              class="btn btn--primary btn--lg"
              @click="registrarCosecha(siembra.id_siembra)"
              title="Registrar Cosecha"
            >
              Registrar Cosecha
            </button>
          </div>
        </article>
      </div>
    </div>

    <!-- Botón siguiente -->
    <button
      class="nav-btn nav-btn--next"
      type="button"
      :disabled="!canNext"
      @click="next"
      aria-label="Siguiente"
      title="Siguiente"
    >
      ›
    </button>

    <!-- Indicadores -->
    <div v-if="totalSlides > 0 && perView < totalSlides" class="dots">
      <button
        v-for="i in pageCount"
        :key="i"
        class="dot"
        :class="{ active: currentPage === (i-1) }"
        @click="goToPage(i-1)"
        :aria-label="`Ir a grupo ${i}`"
        type="button"
      />
    </div>

    <!-- Vacío -->
    <div v-if="totalSlides === 0" class="empty">
      No hay siembras activas que coincidan con tu búsqueda.
    </div>
  </section>
</template>

<script>
import axios from '@/services/axios';

export default {
  name: 'SiembrasActivasCosechaCarrusel',
  data() {
    return {
      siembras: [],
      busqueda: '',
      // carrusel
      index: 0,         // índice del primer slide visible
      perView: 3,       // slides visibles (se recalcula por ancho)
      gapPx: 16,        // separación entre tarjetas (coincide con CSS)
      resizeObs: null
    };
  },
  computed: {
    siembrasFiltradas() {
      const filtro = this.busqueda.trim().toLowerCase();
      if (!filtro) return this.siembras;
      return this.siembras.filter(siembra =>
        Object.values(siembra).some(valor =>
          String(valor ?? '').toLowerCase().includes(filtro)
        )
      );
    },
    totalSlides() {
      return this.siembrasFiltradas.length;
    },
    maxIndex() {
      // último índice inicial permitido para que aún se vean perView items
      return Math.max(0, this.totalSlides - this.perView);
    },
    canPrev() { return this.index > 0; },
    canNext() { return this.index < this.maxIndex; },
    currentPage() {
      // página basada en pasos de 1 con perView visible
      return Math.floor(this.index / 1);
    },
    pageCount() {
      // número de "posiciones" válidas (índices iniciales posibles)
      return this.maxIndex + 1;
    },
    trackStyle() {
      // Cada slide ocupa 100/perView %, el desplazamiento es index * (100/perView) %
      const translatePct = (this.index * (100 / this.perView)) * -1;
      return {
        transform: `translateX(${translatePct}%)`
      };
    },
    slideStyle() {
      // Cada tarjeta ocupa exactamente 100/perView% del ancho de la viewport
      return {
        flex: `0 0 calc(100% / ${this.perView})`,
        maxWidth: `calc(100% / ${this.perView})`
      };
    }
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
          .filter(s => s.estado === 1 && s.acuicola === user?.acuicola)
          .map(s => {
            const estanque = estanques.find(e => e.id_estanque === s.estanque) || {};
            return {
              ...s,
              estanque_nombre: estanque.nombre || '',
              estanque_superficie: estanque.superficie ?? '',
              estanque_profundidad: estanque.profundidad ?? '',
              estanque_infraestructura: estanque.infraestructura || '',
              estanque_ubicacion: estanque.ubicacion || ''
            };
          });

        // al cargar datos, reseteamos al inicio
        this.index = 0;
      } catch (error) {
        console.error('Error al obtener siembras o estanques:', error);
      }
    },
    registrarCosecha(id) {
      this.$router.push(`/producción/cosecha/registro/${id}`);
    },
    // Carrusel
    prev() { if (this.canPrev) this.index -= 1; },
    next() { if (this.canNext) this.index += 1; },
    goToStart() { this.index = 0; },
    goToPage(p) {
      this.index = Math.min(Math.max(p, 0), this.maxIndex);
    },
    computePerView() {
      const w = window.innerWidth;
      // 1 móvil, 2 tablet, 3 escritorio
      this.perView = w < 640 ? 1 : (w < 1024 ? 2 : 3);
      // al cambiar perView, aseguramos no exceder
      this.index = Math.min(this.index, this.maxIndex);
    },
    onResize() {
      this.computePerView();
    }
  },
  mounted() {
    this.obtenerSiembras();
    this.computePerView();
    // Observa cambios de tamaño para recalcular perView
    this.resizeObs = new ResizeObserver(this.onResize);
    this.resizeObs.observe(document.documentElement);
  },
  beforeUnmount() {
    if (this.resizeObs) this.resizeObs.disconnect();
  }
};
</script>

<style scoped>
/* ====== Carrusel ====== */
.carousel {
  position: relative;
  padding: 0 40px; /* espacio para flechas */
  outline: none; /* para el focus por teclado */
}

.viewport {
  overflow: hidden;
  width: 100%;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-lg, 14px);
  background: var(--color-surface, #fff);
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,.10));
}

.track {
  display: flex;
  transition: transform .35s ease;
  will-change: transform;
  gap: 16px; /* ¡IMPORTANTE! Debe coincidir con gapPx si vas a calcular con px */
  padding: 16px;
}

.slide {
  /* anchura se fija dinámicamente con slideStyle (flex-basis/max-width) */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.meta p { margin: 6px 0; font-size: 0.95rem; }

/* Flechas */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 36px; height: 36px;
  border: none; border-radius: 50%;
  background: rgba(0,0,0,.25);
  color: #fff; font-size: 22px; line-height: 1;
  display: grid; place-items: center;
  cursor: pointer;
  transition: background .2s ease, transform .1s ease;
  z-index: 2;
}
.nav-btn:hover { background: rgba(0,0,0,.35); transform: translateY(-50%) scale(1.03); }
.nav-btn:disabled { opacity: .35; cursor: not-allowed; }
.nav-btn--prev { left: 4px; }
.nav-btn--next { right: 4px; }

/* Dots */
.dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 10px;
}
.dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #cbd5e1; border: none; cursor: pointer;
}
.dot.active { background: #8d2a2a; }

/* Vacío */
.empty {
  text-align: center;
  color: var(--color-muted, #6b7280);
  margin-top: 12px;
}

/* Responsivo (coincide con computePerView) */
@media (max-width: 1023px) {
  .carousel { padding: 0 36px; }
}
@media (max-width: 639px) {
  .carousel { padding: 0 30px; }
}
</style>
