<template>
  <section class="card">
    <div class="card__header">
      <h2 class="card__title">Alimentación</h2>
      <p class="card__sub">Registra alimento, lote y cantidad para la siembra seleccionada.</p>
    </div>

    <form class="form" @submit.prevent="submitForm" novalidate>
      <!-- Producto -->
      <div class="field">
        <label for="producto">Alimento</label>
        <select
          id="producto"
          class="select"
          v-model="productoSeleccionado"
          :disabled="cargandoProductos"
          required
        >
          <option value="" disabled>
            {{ cargandoProductos ? 'Cargando alimentos…' : 'Seleccione un alimento' }}
          </option>
          <option
            v-for="p in productosAlimento"
            :key="p.id"
            :value="p.id"
          >
            {{ p.nombre }} · {{ p.porcentaje_proteina ?? '—' }}% · {{ p.presentacion || '—' }}
          </option>
        </select>
        <small v-if="!cargandoProductos && productosAlimento.length === 0" class="text-muted">
          No hay productos del rubro “Alimento”.
        </small>
      </div>

      <!-- Lote -->
      <div class="field">
        <label for="lote">Lote</label>
        <select
          id="lote"
          class="select"
          v-model="loteSeleccionado"
          :disabled="!productoSeleccionado || cargandoLotes"
          required
        >
          <option value="" disabled>
            {{
              !productoSeleccionado
                ? 'Seleccione un alimento primero'
                : (cargandoLotes ? 'Cargando lotes…' : 'Seleccione un lote')
            }}
          </option>
          <option
            v-for="l in lotes"
            :key="l.id"
            :value="l.id"
          >
            {{ l.etiqueta }}
          </option>
        </select>
        <small v-if="productoSeleccionado && !cargandoLotes && lotes.length === 0" class="text-muted">
          Este producto no tiene lotes registrados.
        </small>
      </div>

      <!-- Cantidad -->
      <div class="field">
        <label for="kg">Cantidad de alimento (kg)</label>
        <input
          id="kg"
          class="input"
          type="number"
          step="0.01"
          min="0"
          v-model.number="registro.kg"
          placeholder="0.00"
          required
        />
      </div>

      <!-- Supervivencia -->
      <div class="field">
        <label for="supervivencia">% supervivencia (opcional)</label>
        <input
          id="supervivencia"
          class="input"
          type="number"
          step="0.01"
          min="0"
          max="100"
          v-model.number="registro.supervivencia"
          placeholder="Ej. 98"
        />
      </div>

      <!-- Clima -->
      <div class="field">
        <label for="clima">Clima (opcional)</label>
        <input
          id="clima"
          class="input"
          type="text"
          v-model.trim="registro.clima"
          placeholder="Condición climática"
        />
      </div>

      <!-- Observación -->
      <div class="field">
        <label for="observacion">Comentarios (opcional)</label>
        <textarea
          id="observacion"
          class="textarea"
          rows="3"
          v-model.trim="registro.observacion"
          placeholder="Notas u observaciones"
        ></textarea>
      </div>

      <div class="actions">
        <button class="btn btn--accent btn--lg" type="submit" :disabled="guardando">
          <span v-if="!guardando">Registrar Alimentación</span>
          <span v-else>Guardando…</span>
        </button>
      </div>
    </form>
  </section>
</template>

<script>
import api from '@/services/axios';

export default {
  name: 'ProduccionAlimentarRegistro',
  props: { id: { type: [String, Number], required: true } },
  data() {
    return {
      siembraId: null,

      // catálogos
      rubros: [],
      productos: [],
      rubroAlimentoId: null,        // id del rubro "Alimento" si existe
      nombreRubroAlimento: 'alimento', // fallback por nombre

      cargandoProductos: false,

      // selección
      productoSeleccionado: '',
      lotes: [],
      loteSeleccionado: '',
      cargandoLotes: false,

      // form
      registro: { kg: null, supervivencia: null, clima: '', observacion: '' },
      guardando: false,
    };
  },
  computed: {
    // ✅ Acepta rubro como id, objeto o texto
    productosAlimento() {
      const wantedId = this.rubroAlimentoId != null ? Number(this.rubroAlimentoId) : null;
      const wantedName = this.nombreRubroAlimento;

      const isAlimento = (p) => {
        // 1) rubro id directo (rubro_id o rubro numérico)
        const rid = p?.rubro_id ?? (typeof p?.rubro === 'number' ? p.rubro : null);
        if (rid != null && wantedId != null && Number(rid) === wantedId) return true;

        // 2) rubro como objeto { id, nombre }
        if (p?.rubro && typeof p.rubro === 'object') {
          if (wantedId != null && Number(p.rubro.id ?? p.rubro.id_rubro) === wantedId) return true;
          const n = String(p.rubro.nombre ?? '').toLowerCase().trim();
          if (n === wantedName) return true;
        }

        // 3) rubro como string "Alimento"
        const rname = String(p?.rubro ?? '').toLowerCase().trim();
        if (rname && rname === wantedName) return true;

        return false;
      };

      return this.productos.filter(isAlimento);
    },

    loteSeleccionadoObj() {
      return this.lotes.find(l => l.id === this.loteSeleccionado);
    },
  },
  watch: {
    productoSeleccionado(newVal) {
      this.loteSeleccionado = '';
      this.lotes = [];
      if (newVal) this.cargarLotesDeProducto(newVal);
    },
  },
  methods: {
    async cargarRubrosYProductos() {
      this.cargandoProductos = true;
      try {
        const [rubrosRes, prodRes] = await Promise.all([
          api.get('/rubro/'),
          api.get('/producto/'),
        ]);

        this.rubros = Array.isArray(rubrosRes.data) ? rubrosRes.data : [];
        // intenta resolver el id del rubro “Alimento”; si no existe, seguimos
        const rubroAli = this.rubros.find(
          r => String(r?.nombre ?? '').toLowerCase().trim() === this.nombreRubroAlimento
        );
        this.rubroAlimentoId = rubroAli ? (rubroAli.id_rubro ?? rubroAli.id) : null;

        this.productos = Array.isArray(prodRes.data) ? prodRes.data : [];
      } catch (e) {
        console.error('Error cargando rubros/productos:', e);
        this.rubros = [];
        this.productos = [];
        this.rubroAlimentoId = null; // forzamos a que pase por nombre
      } finally {
        this.cargandoProductos = false;
      }
    },

    async cargarLotesDeProducto(productoId) {
      this.cargandoLotes = true;
      try {
        // DRF: EntradaUnitariaViewSet acepta ?producto_id=
        const { data } = await api.get('/entradaunitaria/', { params: { producto_id: productoId } });
        const filas = Array.isArray(data) ? data : [];
        this.lotes = [...new Map(
          filas
            .filter(eu => eu && (eu.lote ?? '').toString().trim() !== '')
            .map(eu => ([
              (eu.id ?? eu.id_entradaunitaria ?? eu.pk),
              { id: (eu.id ?? eu.id_entradaunitaria ?? eu.pk), etiqueta: eu.lote }
            ]))
        ).values()];
      } catch (e) {
        console.error('Error cargando lotes:', e);
        this.lotes = [];
      } finally {
        this.cargandoLotes = false;
      }
    },

    async submitForm() {
      if (!this.productoSeleccionado) { alert('Seleccione un alimento.'); return; }
      if (!this.loteSeleccionado) { alert('Seleccione un lote.'); return; }
      if (this.registro.kg == null || this.registro.kg < 0) { alert('Ingrese kg válidos.'); return; }

      this.guardando = true;
      try {
        const payload = {
          siembra: Number(this.siembraId),
          producto: Number(this.productoSeleccionado),
          lote_id: this.loteSeleccionado,
          lote: this.loteSeleccionadoObj?.etiqueta ?? '',
          kg: Number(this.registro.kg),
          supervivencia: this.registro.supervivencia != null ? Number(this.registro.supervivencia) : null,
          clima: this.registro.clima || '',
          observacion: this.registro.observacion || '',
        };
        await api.post('/alimentar/', payload);
        alert('¡Registro de alimentación guardado!');
        this.$router.push('/producción/alimentar');
      } catch (e) {
        console.error('Error al guardar:', e);
        alert(e?.response?.data?.detail || 'No fue posible guardar.');
      } finally {
        this.guardando = false;
      }
    },
  },
  mounted() {
    this.siembraId = Number(this.id);
    this.cargarRubrosYProductos();
  },
};
</script>

<style scoped>
.form { display: grid; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.input, .select, .textarea {
  width: 100%; padding: 10px 12px;
  background: #f8f9fa; color: var(--color-text, #1f2937);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 10px;
  font-size: 14px; transition: border-color .2s ease, box-shadow .2s ease, background .2s ease;
}
.input:focus, .select:focus, .textarea:focus {
  outline: none; background: #fff;
  box-shadow: 0 0 0 3px rgba(63,85,194,.2);
  border-color: #3f55c2;
}
.actions { margin-top: 6px; }
.text-muted { color: #6b7280; }
.btn--accent {
  background: var(--color-accent, #7f1d1d);
  color: #fff;
}
</style>
