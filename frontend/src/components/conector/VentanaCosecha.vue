<template>
  <!-- Encabezado + buscador -->
  <section class="card">
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
      />
    </div>
  </section>

  <!-- Grilla de tarjetas -->
  <section class="container">
    <div class="list-grid">
      <article
        v-for="siembra in siembrasFiltradas"
        :key="siembra.id_siembra"
        class="card"
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
  </section>
</template>

<script>
import axios from '@/services/axios';

export default {
  name: 'SiembrasActivasCosecha',
  data() {
    return {
      siembras: [],
      busqueda: ''
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
          .filter(s => s.estado === 1 && s.acuicola === user.acuicola)
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

      } catch (error) {
        console.error('Error al obtener siembras o estanques:', error);
      }
    },
    registrarCosecha(id) {
      this.$router.push(`/producción/cosecha/registro/${id}`);
    }
  },
  mounted() {
    this.obtenerSiembras();
  }
};
</script>

<style scoped>
/* Grilla responsiva para las tarjetas usando el tema global */
.list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}
/* Ajustes finos al contenido dentro de las tarjetas */
.meta p {
  margin: 6px 0;
  font-size: 0.95rem;
}
</style>
