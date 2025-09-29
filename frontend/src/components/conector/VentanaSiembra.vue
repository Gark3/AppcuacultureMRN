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
    // ---------- Normalizadores ----------
    getIdEstanque(obj) {
      const raw = obj?.id_estanque ?? obj?.id ?? obj;
      return raw == null || raw === '' ? null : Number(raw);
    },
    getIdAcuicola(obj) {
      if (obj && typeof obj === 'object') {
        const raw = obj.id ?? obj.id_acuicola ?? obj.acuicola ?? null;
        return raw == null || raw === '' ? null : Number(raw);
      }
      return obj == null || obj === '' ? null : Number(obj);
    },
    // Siembra ACTIVA según tu regla: estado = 1 y estatus = 0
    isSiembraActiva(s) {
      const estado  = Number(s?.estado ?? 0);
      const estatus = Number(s?.estatus ?? 0);
      return estado === 1 && estatus === 0;
    },

    // ---------- Obtener acuícola del usuario ----------
    async resolveUserAcuicolaId() {
      const user = JSON.parse(localStorage.getItem('user') || '{}');

      // Si ya viene en el objeto user, úsalo
      const direct =
        user?.acuicola ??
        user?.acuicola_id ??
        user?.perfil?.acuicola ??
        user?.perfil?.acuicola_id ??
        user?.perfil?.acuicola?.id;

      if (Number.isFinite(Number(direct))) {
        return Number(direct);
      }

      // Fallback: pedimos /perfil/ y tomamos el primero (el backend ya filtra por el usuario autenticado)
      try {
        const { data } = await api.get('/perfil/');
        const perfil = Array.isArray(data) ? data[0] : data;
        const ac =
          perfil?.acuicola ??
          perfil?.acuicola_id ??
          perfil?.acuicola?.id;
        return Number(ac);
      } catch (e) {
        console.warn('No se pudo resolver el acuícola desde /perfil/.', e);
        return NaN;
      }
    },

    // ---------- Carga de estanques ----------
    async obtenerEstanques() {
      this.cargando = true;
      this.error = null;
      try {
        const userAcuicolaId = await this.resolveUserAcuicolaId();
        if (!Number.isFinite(userAcuicolaId)) {
          this.estanques = [];
          this.error = 'No fue posible determinar el acuícola del usuario.';
          return;
        }

        const [estanquesResp, siembrasResp] = await Promise.all([
          api.get('/estanque/'),
          api.get('/siembra/'),
        ]);

        const todosEstanques = Array.isArray(estanquesResp.data) ? estanquesResp.data : [];
        const todasSiembras  = Array.isArray(siembrasResp.data)  ? siembrasResp.data  : [];

        // Estanques ocupados por siembras ACTIVAS de MI acuícola (estado=1, estatus=0)
        const ocupados = new Set(
          todasSiembras
            .filter((s) => {
              const acSiembra = Number(s.acuicola_id ?? s.acuicola);
              return this.isSiembraActiva(s) && acSiembra === userAcuicolaId;
            })
            .map((s) => Number(s.estanque_id ?? this.getIdEstanque(s.estanque)))
            .filter((id) => Number.isFinite(id))
        );

        // Disponibles: de mi acuícola, activos (estatus true) y no ocupados
        this.estanques = todosEstanques.filter((e) => {
          const ac = Number(e.acuicola);     // tu /estanque/ lo trae como número
          const activo = e.estatus === true; // del JSON
          const idE = this.getIdEstanque(e); // id_estanque

          if (!Number.isFinite(idE)) return false;
          if (ac !== userAcuicolaId) return false;
          if (!activo) return false;

          return !ocupados.has(idE);
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
