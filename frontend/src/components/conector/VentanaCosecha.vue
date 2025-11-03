<template>
  <section
    class="carousel container container--fluid"
    :class="{ 'carousel--compact': totalSlides <= visible }"
    ref="carouselEl"
    @keydown.left.prevent="prev"
    @keydown.right.prevent="next"
    tabindex="0"
  >
    <!-- Pista -->
    <div class="viewport">
      <div
        class="track"
        :style="{
          transform: `translateX(-${translatePercent}%)`,
          gap: gapPx + 'px'
        }"
      >
        <div
          v-for="(s, i) in siembrasFiltradas"
          :key="s.id_siembra || i"
          class="slide"
          :style="slideStyle"
        >
          <!-- Tarjeta (tu card original) -->
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
                @click="$emit('registrar', s.id_siembra)"
              >
                Registrar Cosecha
              </button>
            </div>
          </article>
        </div>
      </div>

      <!-- Flechas (solo si hay más ítems que visibles) -->
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
export default {
  name: 'CarruselSiembras',
  props: {
    siembrasFiltradas: { type: Array, required: true },
    gap: { type: Number, default: 16 },           // separación entre slides (px)
    perViewDesktop: { type: Number, default: 3 }, // >=1024px
    perViewTablet: { type: Number, default: 2 },  // 640–1023px
    perViewMobile: { type: Number, default: 1 }   // <640px
  },
  data() {
    return {
      index: 0,
      vw: typeof window !== 'undefined' ? window.innerWidth : 1280
    };
  },
  computed: {
    totalSlides() { return this.siembrasFiltradas?.length || 0; },
    visible() {
      if (this.vw < 640) return this.perViewMobile;
      if (this.vw < 1024) return this.perViewTablet;
      return this.perViewDesktop;
    },
    // cuántas “páginas” hay si avanzamos de 1 en 1
    maxIndex() {
      return Math.max(0, this.totalSlides - this.visible);
    },
    canPrev() { return this.index > 0; },
    canNext() { return this.index < this.maxIndex; },
    pageIndex() { return Math.floor(this.index); },
    pageCount() { return Math.max(1, this.totalSlides - this.visible + 1); },
    gapPx() { return this.gap; },
    // ancho exacto de cada slide: reparte 100% restando los gaps internos
    slideStyle() {
      const v = Math.max(1, Math.min(this.visible, this.totalSlides || 1));
      // total gap por “fila” = gap * (v - 1)
      // ancho disponible = 100% - esos gaps
      return {
        flex: `0 0 calc((100% - ${this.gapPx * (v - 1)}px) / ${v})`,
        maxWidth: `calc((100% - ${this.gapPx * (v - 1)}px) / ${v})`
      };
    },
    // porcentaje a desplazar por avance de 1 tarjeta
    translatePercent() {
      const v = Math.max(1, Math.min(this.visible, this.totalSlides || 1));
      return (this.index * 100) / v;
    }
  },
  methods: {
    prev() { if (this.canPrev) this.index -= 1; },
    next() { if (this.canNext) this.index += 1; },
    goToPage(p) {
      // posiciona para que el primer slide visible sea p
      this.index = Math.max(0, Math.min(p, this.maxIndex));
    },
    onResize() {
      this.vw = window.innerWidth;
      // corrige índice si el visible cambió y quedó fuera de rango
      if (this.index > this.maxIndex) this.index = this.maxIndex;
    }
  },
  mounted() {
    this.onResize();
    window.addEventListener('resize', this.onResize, { passive: true });
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.onResize);
  }
};
</script>

<style scoped>
/* Que el carrusel pueda ocupar el 100% horizontal */
.container.container--fluid { max-width: 100% !important; }

/* Estructura */
.carousel { outline: none; }
.viewport {
  position: relative;
  width: 100%;
  overflow: hidden;              /* oculta desbordes laterales */
  border-radius: var(--radius-lg, 14px);
  background: var(--color-surface, #fff);
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,.10));
}
.track {
  display: flex;
  width: 100%;
  will-change: transform;
  transition: transform .28s ease;
  padding: 20px;                 /* respiro interior */
  box-sizing: border-box;
}

/* Cada slide ocupa exactamente su porción calculada */
.slide { display: flex; }

/* Tarjeta: misma altura para que nada “salte” */
.card--fill {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}
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

/* Centrar cuando hay 1–2 tarjetas y no se necesitan flechas */
.carousel--compact .track { justify-content: center; }

/* Responsivo: 1 por 1 en móvil ya controlado por visible, aquí afinamos UI */
@media (max-width: 640px) {
  .track { padding: 14px; }
  .nav-btn { width: 36px; height: 36px; font-size: 20px; }
}
</style>
