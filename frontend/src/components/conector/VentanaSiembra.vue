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
        :key="getIdEstanque(estanque)"
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
            @click="irAFormularioSiembra(getIdEstanque(estanque))"
            title="Usar este estanque para siembra"
          >
            Utilizar Estanque
          </button>
        </div>
      </article>
    </div>

    <p v-if="cargando" class="text-muted mt-3">Cargando estanques…</p>
    <p v-else-if="!estanquesFiltrados.length" class="text-muted mt-3">
      No hay estanques disponibles para siembra.
    </p>
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
  },
  methods: {
    // PK puede llamarse "id" o "id_estanque"
    getIdEstanque(e) {
      const id = e?.id ?? e?.id_estanque ?? null;
      return id == null ? null : Number(id);
    },
    // acuícola puede venir como ID o como objeto
    getIdAcuicola(a) {
      const id = (a && typeof a === 'object') ? (a.id ?? a.id_acuicola ?? null) : a;
      return id == null ? null : Number(id);
    },
    // Detecta si una siembra está activa (varios formatos posibles)
    isSiembraActiva(s) {
      if (typeof s.estatus !== 'undefined') return !!s.estatus;
      if (typeof s.estado !== 'undefined') return Number(s.estado) === 1;
      if (typeof s.finalizada !== 'undefined') return !s.finalizada;
      if ('fecha_fin' in s) return !s.fecha_fin;
      return false;
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

        // 1) Traer siembras y estanques
        const [siembrasResp, estanquesResp] = await Promise.all([
          api.get('/siembra/'),
          api.get('/estanque/'),
        ]);

        const todasSiembras = Array.isArray(siembrasResp.data) ? siembrasResp.data : [];
        const todosEstanques = Array.isArray(estanquesResp.data) ? estanquesResp.data : [];

        // 2) Construir set de estanques con siembra activa en mi acuícola
        const ocupados = new Set(
          todasSiembras
            .filter((s) => this.isSiembraActiva(s) && this.getIdAcuicola(s.acuicola) === userAcuicolaId)
            .map((s) => this.getIdEstanque(s.estanque))
            .filter((id) => id != null)
        );

        // 3) Filtrar estanques: de mi acuícola, activos (si aplica) y no ocupados
        this.estanques = todosEstanques.filter((e) => {
          const acuicolaId = this.getIdAcuicola(e.acuicola);
          if (acuicolaId !== userAcuicolaId) return false;

          // si tu modelo tiene "estatus" en Estanque, respétalo
          const activo = (typeof e.estatus !== 'undefined') ? !!e.estatus : true;
          if (!activo) return false;

          const idEstanque = this.getIdEstanque(e);
          return idEstanque != null && !ocupados.has(idEstanque);
        });
      } catch (error) {
        console.error('Error al obtener estanques:', error);
        this.error = 'No se pudo cargar la lista de estanques.';
        this.estanques = [];
      } finally {
        this.cargando = false;
      }
    },

    irAFormularioSiembra(estanqueId) {
      // ⚠️ Si tu ruta real no lleva acento, usa /produccion/
      this.$router.push(`/producción/siembra/registro/${estanqueId}`);
      // this.$router.push(`/produccion/siembra/registro/${estanqueId}`);
    },
  },

  mounted() {
    this.obtenerEstanques();
  },
};
</script>

<style scoped>
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
