<template>
  <section class="card">
    <div class="card__header">
      <h2 class="card__title">Lista de Estanques</h2>
      <p class="card__sub">Selecciona un estanque para ir a Calidad del Agua.</p>
    </div>

    <div v-if="estanques.length" class="pond-grid">
      <button
        v-for="e in estanques"
        :key="e.id_estanque ?? e.id"
        class="btn btn--primary btn--lg"
        @click="irACalidadAgua(e.id_estanque ?? e.id)"
      >
        {{ e.nombre || 'Sin nombre' }}
      </button>
    </div>

    <p v-else class="text-muted">Cargando estanques…</p>
  </section>
</template>

<script>
import axios from '@/services/axios';

export default {
  name: 'ListaEstanques',
  data() {
    return {
      estanques: []
    };
  },
  mounted() {
    this.obtenerEstanques();
  },
  methods: {
    async obtenerEstanques() {
      try {
        const res = await axios.get('/estanque/');
        this.estanques = res.data || [];
      } catch (error) {
        console.error('Error al obtener estanques:', error);
      }
    },
    irACalidadAgua(id) {
      // Ajusta la ruta si tu módulo de calidad vive bajo /producción
      // this.$router.push({ path: '/producción/calidad-agua', query: { estanque_id: id } });
      this.$router.push({ path: '/calidad-agua', query: { estanque_id: id } });
    }
  }
};
</script>

<style scoped>
/* Grilla responsiva para los botones usando el tema global */
.pond-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}
</style>
