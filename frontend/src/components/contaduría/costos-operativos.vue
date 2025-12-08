<template>
  <section class="costos">
    <div class="card">
      <header class="card__header">
        <h2 class="card__title">Costos Operativos</h2>
        <p class="card__sub">
          Registra gastos generales de la granja o asociados a un ciclo de siembra.
        </p>
      </header>

      <!-- FORMULARIO -->
      <form class="form" @submit.prevent="registrarGasto">
        <!-- Tipo de gasto -->
        <div class="field">
          <label class="label" for="tipo">Tipo de gasto</label>
          <select
            id="tipo"
            class="input"
            v-model="nuevoGasto.tipo"
            required
          >
            <option disabled value="">Seleccione</option>
            <option
              v-for="tipo in tiposGasto"
              :key="tipo.id"
              :value="tipo.id"
            >
              {{ tipo.nombre }}
            </option>
          </select>
        </div>

        <!-- Descripción -->
        <div class="field">
          <label class="label" for="descripcion">Descripción</label>
          <textarea
            id="descripcion"
            class="input input--textarea"
            v-model="nuevoGasto.descripcion"
            rows="3"
            required
          ></textarea>
        </div>

        <!-- Monto -->
        <div class="field field--inline">
          <div class="field">
            <label class="label" for="monto">Monto</label>
            <input
              id="monto"
              type="number"
              class="input"
              v-model.number="nuevoGasto.monto"
              step="0.01"
              min="0"
              required
            />
          </div>

          <div class="field field--checkbox">
            <label class="checkbox">
              <input
                type="checkbox"
                v-model="nuevoGasto.es_general"
              />
              <span>Gasto general (se reparte entre todos los ciclos activos)</span>
            </label>
          </div>
        </div>

        <!-- Ciclo de siembra (solo si NO es general) -->
        <div
          class="field"
          v-if="!nuevoGasto.es_general"
        >
          <label class="label" for="siembra">Ciclo de siembra</label>
          <select
            id="siembra"
            class="input"
            v-model="nuevoGasto.siembra"
            :required="!nuevoGasto.es_general"
          >
            <option disabled value="">Seleccione un ciclo activo</option>
            <option
              v-for="ciclo in ciclosActivos"
              :key="ciclo.id_siembra"
              :value="ciclo.id_siembra"
            >
              Estanque {{ ciclo.estanque_nombre }} · {{ ciclo.etapa || 'Sin etapa' }}
            </option>
          </select>
          <p class="text-muted small" v-if="!ciclosActivos.length">
            No hay ciclos activos en esta acuícola.
          </p>
        </div>

        <!-- Botón -->
        <div class="field field--actions">
          <button
            type="submit"
            class="btn btn--primary"
            :disabled="loading"
          >
            {{ loading ? 'Guardando…' : 'Registrar gasto' }}
          </button>
        </div>
      </form>
    </div>

    <!-- HISTORIAL -->
    <div class="card card--mt">
      <header class="card__header card__header--compact">
        <h3 class="card__title">Historial de gastos</h3>
        <p class="card__sub" v-if="gastosNormalizados.length">
          {{ gastosNormalizados.length }} registro(s)
        </p>
      </header>

      <div v-if="!gastosNormalizados.length" class="empty-state">
        <p>No hay gastos registrados.</p>
      </div>

      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Tipo</th>
              <th>Descripción</th>
              <th>Monto</th>
              <th>Alcance</th>
              <th>Ciclo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="g in gastosNormalizados" :key="g.id">
              <td>{{ formatFecha(g.fecha) }}</td>
              <td>{{ g.tipoNombre }}</td>
              <td>{{ g.descripcion }}</td>
              <td class="text-right">{{ formatMoneda(g.monto) }}</td>
              <td>{{ g.esGeneral ? 'General' : 'Específico' }}</td>
              <td>
                <span v-if="!g.esGeneral && g.siembra">
                  #{{ g.siembra }}
                </span>
                <span v-else class="text-muted">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script>
import axios from '@/services/axios';

export default {
  name: 'CostosOperativos',
  data() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return {
      usuarioId: user?.usuario_id ?? null,
      acuicolaId: user?.acuicola ?? null,

      tiposGasto: [],
      ciclosActivos: [],
      gastos: [],           // crudo desde API
      loading: false,

      nuevoGasto: {
        tipo: '',
        descripcion: '',
        monto: 0,
        es_general: false,
        siembra: '',
      },
    };
  },
  computed: {
    tiposMap() {
      const map = {};
      this.tiposGasto.forEach(t => {
        const id = t.id ?? t.id_tipo_gasto;
        map[id] = t.nombre;
      });
      return map;
    },
    gastosNormalizados() {
      return (this.gastos || []).map(g => {
        const id = g.id ?? g.id_gasto;
        const tipoId =
          typeof g.tipo === 'object'
            ? (g.tipo.id ?? g.tipo.id_tipo_gasto)
            : g.tipo;
        const tipoNombre =
          typeof g.tipo === 'object'
            ? (g.tipo.nombre || this.tiposMap[tipoId] || 'Sin tipo')
            : this.tiposMap[tipoId] || 'Sin tipo';

        const siembraId =
          typeof g.siembra === 'object'
            ? (g.siembra.id_siembra ?? g.siembra.id)
            : g.siembra ?? null;

        const esGeneral =
          g.es_general ?? g.general ?? (siembraId === null || siembraId === undefined);

        return {
          id,
          tipoId,
          tipoNombre,
          descripcion: g.descripcion ?? '',
          monto: Number(g.monto) || 0,
          fecha: g.fecha || g.created_at || g.fecha_registro || null,
          esGeneral,
          siembra: siembraId,
        };
      });
    },
  },
  methods: {
    async cargarCatalogos() {
      try {
        const [resTipos, resSiembras, resGastos] = await Promise.all([
          axios.get('/tipo-gasto/'),
          axios.get('/siembra/'),
          axios.get('/gasto/'),
        ]);

        const tiposRaw = Array.isArray(resTipos.data)
          ? resTipos.data
          : (resTipos.data.results || []);
        const siembrasRaw = Array.isArray(resSiembras.data)
          ? resSiembras.data
          : (resSiembras.data.results || []);
        const gastosRaw = Array.isArray(resGastos.data)
          ? resGastos.data
          : (resGastos.data.results || []);

        this.tiposGasto = tiposRaw;

        // ciclos activos = siembra SIN fecha de cosecha y de mi acuícola
        this.ciclosActivos = siembrasRaw.filter(s => {
          const sinCosecha = !s.fecha_cosecha;
          const acuicolaId =
            typeof s.acuicola === 'object'
              ? (s.acuicola.id_acuicola ?? s.acuicola.id)
              : s.acuicola;
          const mismoAcuicola =
            this.acuicolaId == null || acuicolaId === this.acuicolaId;

          return sinCosecha && mismoAcuicola;
        }).map(s => ({
          ...s,
          estanque_nombre:
            (s.estanque && (s.estanque.nombre || s.estanque.estanque_nombre)) ||
            s.estanque_nombre ||
            s.estanque_id ||
            'Estanque',
        }));

        this.gastos = gastosRaw;
      } catch (error) {
        console.error('Error al cargar los datos de costos operativos:', error);
      }
    },

    async registrarGasto() {
      if (!this.nuevoGasto.tipo) {
        alert('Selecciona un tipo de gasto.');
        return;
      }
      if (!this.nuevoGasto.es_general && !this.nuevoGasto.siembra) {
        alert('Selecciona un ciclo de siembra o marca el gasto como general.');
        return;
      }

      try {
        this.loading = true;

        const payload = {
          tipo: this.nuevoGasto.tipo,
          descripcion: this.nuevoGasto.descripcion,
          monto: this.nuevoGasto.monto,
          es_general: this.nuevoGasto.es_general,
          siembra: this.nuevoGasto.es_general ? null : this.nuevoGasto.siembra,
          usuario: this.usuarioId,
          acuicola: this.acuicolaId,
          estado: 1,
        };

        await axios.post('/gasto/', payload);

        this.limpiarFormulario();
        await this.cargarCatalogos();

        alert('Gasto registrado con éxito.');
      } catch (error) {
        console.error('Error al registrar el gasto:', error);
        alert('Ocurrió un error al registrar el gasto.');
      } finally {
        this.loading = false;
      }
    },

    limpiarFormulario() {
      this.nuevoGasto = {
        tipo: '',
        descripcion: '',
        monto: 0,
        es_general: false,
        siembra: '',
      };
    },

    formatMoneda(valor) {
      const n = Number(valor) || 0;
      return n.toLocaleString('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 2,
      });
    },

    formatFecha(fecha) {
      if (!fecha) return '—';
      const d = new Date(fecha);
      if (isNaN(d.getTime())) return fecha;
      return d.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      });
    },
  },
  mounted() {
    this.cargarCatalogos();
  },
};
</script>

<style scoped>
.costos {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px 10px 40px;
}

.card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
  padding: 20px 20px 24px;
}

.card--mt {
  margin-top: 24px;
}

.card__header {
  margin-bottom: 18px;
}

.card__header--compact {
  margin-bottom: 12px;
}

.card__title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.card__sub {
  margin-top: 4px;
  font-size: 0.9rem;
  color: #6b7280;
}

/* Formulario */
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field--inline {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr);
  gap: 16px;
}

.field--checkbox {
  justify-content: flex-end;
}

.field--actions {
  margin-top: 8px;
  align-items: flex-end;
}

.label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
}

.input {
  border-radius: 8px;
  border: 1px solid #d1d5db;
  padding: 8px 10px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.25);
}

.input--textarea {
  resize: vertical;
  min-height: 80px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #374151;
}

.checkbox input {
  width: 16px;
  height: 16px;
}

/* Botón */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 16px;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.btn--primary {
  background: #2563eb;
  color: #ffffff;
  box-shadow: 0 10px 18px rgba(37, 99, 235, 0.25);
}

.btn--primary:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.btn--primary:disabled {
  opacity: 0.65;
  cursor: default;
  box-shadow: none;
}

/* Tabla historial */
.table-wrap {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.table th,
.table td {
  padding: 8px 10px;
  border-bottom: 1px solid #e5e7eb;
}

.table th {
  text-align: left;
  font-weight: 600;
  color: #4b5563;
  background: #f9fafb;
}

.table tr:nth-child(even) td {
  background: #f9fafb;
}

.text-right {
  text-align: right;
}

.text-muted {
  color: #9ca3af;
}

.small {
  font-size: 0.78rem;
}

.empty-state {
  padding: 12px 4px 8px;
  font-size: 0.9rem;
  color: #6b7280;
}
</style>
