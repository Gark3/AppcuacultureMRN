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
import api from '@/services/axios'; // tu wrapper de axios

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
        Object.values(e).some((valor) =>
          String(valor ?? '').toLowerCase().includes(filtro)
        )
      );
    },
  },
  methods: {
    // —————————————————————————————————————
    // Helpers de normalización
    // —————————————————————————————————————
    getIdEstanque(e) {
      // PK puede llamarse "id" o "id_estanque"
      return e?.id ?? e?.id_estanque ?? null;
    },
    getIdAcuicola(a) {
      // Puede venir como id o como objeto
      if (a && typeof a === 'object') {
        return a.id ?? a.id_acuicola ?? null;
      }
      return a ?? null;
    },
    isSiembraActiva(s) {
      // Trata de adivinar el campo de "activo"
      // Ajusta si tu modelo usa uno específico
      if (typeof s.estatus !== 'undefined') return !!s.estatus;
      if (typeof s.estado !== 'undefined') return s.estado === 1 || s.estado === '1' || s.estado === true;
      if (typeof s.finalizada !== 'undefined') return !s.finalizada;
      if ('fecha_fin' in s) return !s.fecha_fin;
      // Si no sabemos, por seguridad consideramos que NO está activa
      return false;
    },

    // —————————————————————————————————————
    // Carga de estanques
    // —————————————————————————————————————
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

        // 1) PRIMERA OPCIÓN: si existe el endpoint del back que ya devuelve disponibles
        try {
          const { data } = await api.get('/estanque/disponibles/');
          // Si responde un array, úsalo tal cual y sal
          if (Array.isArray(data)) {
            this.estanques = data;
            return;
          }
        } catch (e) {
          // Si 404/405/… seguimos con el filtrado en el front
          // console.warn('No existe /estanque/disponibles/. Filtramos en front.', e);
        }

        // 2) BACKUP: filtrado en el front
        const [estanquesResp, siembrasResp] = await Promise.all([
          api.get('/estanque/'),
          api.get('/siembra/'),
        ]);

        const todosEstanques = Array.isArray(estanquesResp.data) ? estanquesResp.data : [];
        const todasSiembras  = Array.isArray(siembrasResp.data) ? siembrasResp.data : [];

        // Set con ids de estanques que tienen siembra ACTIVA
        const estanquesConSiembraActiva = new Set(
          todasSiembras
            .filter((s) => this.isSiembraActiva(s) && this.getIdAcuicola(s.acuicola) === user.acuicola)
            .map((s) => this.getIdEstanque(s.estanque))
            .filter((id) => id != null)
        );

        // Filtra por: misma acuícola y que NO estén en el set de activos
        this.estanques = todosEstanques.filter((e) => {
          const acuicolaId = this.getIdAcuicola(e.acuicola);
          const idEstanque = this.getIdEstanque(e);
          if (acuicolaId !== user.acuicola) return false;
          if (idEstanque == null) return false;

          // Si también tienes un booleano de "estatus" en Estanque, puedes respetarlo:
          // const activo = (typeof e.estatus !== 'undefined') ? !!e.estatus : true;
          // if (!activo) return false;

          return !estanquesConSiembraActiva.has(idEstanque);
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
