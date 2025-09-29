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
      } catch (error) {
        console.error('Error al obtener estanques:', error);
        this.error = 'No se pudo cargar la lista de estanques.';
        this.estanques = [];
      } finally {
        this.cargando = false;
      }
    },

    irAFormularioSiembra(estanqueId) {
      // Si tu router no usa acento, cambia a /produccion/...
      this.$router.push(`/producción/siembra/registro/${estanqueId}`);
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
