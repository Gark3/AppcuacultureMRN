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

  <!-- Grilla de tarjetas con estanques disponibles -->
  <section class="container">
    <div class="list-grid">
      <article
        v-for="estanque in estanquesFiltrados"
        :key="estanque.id_estanque"
        class="card"
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

        <div class="mt-3">
          <button
            class="btn btn--accent btn--lg"
            @click="irAFormularioSiembra(estanque.id_estanque)"
            title="Usar este estanque para siembra"
          >
            Utilizar Estanque
          </button>
        </div>
      </article>
    </div>

    <p v-if="!estanques.length" class="text-muted mt-3">Cargando estanques…</p>
  </section>
</template>

<script>
import axios from '@/services/axios';

export default {
  name: 'SeleccionarEstanqueSiembra',
  data() {
    return {
      estanques: [],
      busqueda: ''
    };
  },
  computed: {
    estanquesFiltrados() {
      const filtro = this.busqueda.trim().toLowerCase();
      if (!filtro) return this.estanques;
      return this.estanques.filter((e) =>
        Object.values(e).some((valor) => String(valor ?? '').toLowerCase().includes(filtro))
      );
    }
  },
  methods: {
    // Extrae id cuando acuícola puede venir como objeto o número
    getAcuicolaId(acuicola) {
      return (typeof acuicola === 'object' && acuicola !== null)
        ? acuicola.id_acuicola
        : acuicola;
    },
    // Extrae id cuando estanque puede venir como objeto o número
    getEstanqueId(estanque) {
      return (typeof estanque === 'object' && estanque !== null)
        ? estanque.id_estanque
        : estanque;
    },
    async obtenerEstanques() {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) {
          console.error('No se encontró un usuario en localStorage.');
          this.estanques = [];
          return;
        }

        // 1) Siembras activas para excluir sus estanques
        let siembrasActivas = [];
        try {
          const siembrasResp = await axios.get('/siembra/');
          const todas = siembrasResp.data || [];
          siembrasActivas = todas
            .filter((s) => s.estado === 1 && this.getAcuicolaId(s.acuicola) === user.acuicola)
            .map((s) => this.getEstanqueId(s.estanque));
        } catch (e) {
          console.warn('No se pudieron obtener siembras; se asume 0 activas.', e);
          siembrasActivas = [];
        }

        // 2) Estanques activos de la misma acuícola y no usados en siembra activa
        const estanquesResp = await axios.get('/estanque/');
        const todos = estanquesResp.data || [];
        this.estanques = todos.filter((e) =>
          e.estatus === true &&
          this.getAcuicolaId(e.acuicola) === user.acuicola &&
          !siembrasActivas.includes(e.id_estanque)
        );
      } catch (error) {
        console.error('Error al obtener estanques:', error);
        this.estanques = [];
      }
    },
    irAFormularioSiembra(estanqueId) {
      this.$router.push(`/producción/siembra/registro/${estanqueId}`);
    }
  },
  mounted() {
    this.obtenerEstanques();
  }
};
</script>

<style scoped>
/* Grilla responsiva para tarjetas usando el tema global */
.list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}
.meta p {
  margin: 6px 0;
  font-size: 0.95rem;
}
</style>
