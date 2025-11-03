<template>
  <div class="registro-siembra">
    <h1>Alimentación</h1>

    <form @submit.prevent="submitForm">
      <!-- Alimento -->
      <div class="form-group">
        <label for="alimento">Alimento</label>
        <select
          id="alimento"
          v-model="productoSeleccionado"
          @change="onProductoChange"
          required
        >
          <option value="" disabled>Seleccione un alimento</option>
          <option
            v-for="p in productosAlimento"
            :key="p.id ?? p.id_producto ?? p.pk"
            :value="Number(p.id ?? p.id_producto ?? p.pk)"
          >
            {{ p.nombre }} · {{ p.porcentaje_proteina ?? '—' }}% · {{ p.presentacion ?? '—' }}
          </option>
        </select>
      </div>

      <!-- Lote -->
      <div class="form-group">
        <label for="lote">Lote</label>
        <select
          id="lote"
          v-model="loteSeleccionado"
          :key="productoSeleccionado"          <!-- fuerza limpiar al cambiar alimento -->
          :disabled="cargandoLotes"            <!-- solo se deshabilita mientras carga -->
          required
        >
          <option value="" disabled>
            {{ cargandoLotes
              ? 'Cargando lotes…'
              : (lotes.length ? 'Seleccione un lote' : 'No hay lotes para este alimento') }}
          </option>
          <option
            v-for="l in lotes"
            :key="l.id"
            :value="l.id"
          >
            {{ l.etiqueta }}
          </option>
        </select>
      </div>

      <!-- Cantidad -->
      <div class="form-group">
        <label for="kg">Cantidad de Alimento (kg)</label>
        <input id="kg" type="number" step="0.01" v-model.number="registro.kg" required />
      </div>

      <!-- Opcionales -->
      <div class="form-group">
        <label for="supervivencia">% supervivencia (opcional)</label>
        <input id="supervivencia" type="number" v-model.number="registro.supervivencia" />
      </div>

      <div class="form-group">
        <label for="clima">Clima (opcional)</label>
        <input id="clima" type="text" v-model="registro.clima" />
      </div>

      <div class="form-group">
        <label for="observacion">Comentarios (opcional)</label>
        <textarea id="observacion" v-model="registro.observacion"></textarea>
      </div>

      <button type="submit" :disabled="guardando">
        {{ guardando ? 'Guardando…' : 'Registrar Alimentación' }}
      </button>
    </form>
  </div>
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
      rubroAlimentoId: null,
      nombreRubroAlimento: 'alimento',

      // selección
      productoSeleccionado: '',     // id numérico del producto
      lotes: [],
      loteSeleccionado: '',

      // estados
      cargandoProductos: false,
      cargandoLotes: false,
      guardando: false,

      // form
      registro: { kg: null, supervivencia: null, clima: '', observacion: '' },
    };
  },
  computed: {
    // acepta rubro como id, objeto o string
    productosAlimento() {
      const wantedId = this.rubroAlimentoId != null ? Number(this.rubroAlimentoId) : null;
      const wantedName = this.nombreRubroAlimento;

      const isAlimento = (p) => {
        const rid = p?.rubro_id ?? (typeof p?.rubro === 'number' ? p.rubro : null);
        if (rid != null && wantedId != null && Number(rid) === wantedId) return true;

        if (p?.rubro && typeof p.rubro === 'object') {
          if (wantedId != null && Number(p.rubro.id ?? p.rubro.id_rubro) === wantedId) return true;
          const n = String(p.rubro.nombre ?? '').toLowerCase().trim();
          if (n === wantedName) return true;
        }

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
  methods: {
    async cargarRubrosYProductos() {
      this.cargandoProductos = true;
      try {
        const [rubrosRes, prodRes] = await Promise.all([
          api.get('/rubro/'),
          api.get('/producto/'),
        ]);
        this.rubros = Array.isArray(rubrosRes.data) ? rubrosRes.data : [];
        const rubroAli = this.rubros.find(
          r => String(r?.nombre ?? '').toLowerCase().trim() === this.nombreRubroAlimento
        );
        this.rubroAlimentoId = rubroAli ? (rubroAli.id_rubro ?? rubroAli.id) : null;

        this.productos = Array.isArray(prodRes.data) ? prodRes.data : [];
      } catch (e) {
        console.error('Error cargando rubros/productos:', e);
        this.rubros = [];
        this.productos = [];
        this.rubroAlimentoId = null;
      } finally {
        this.cargandoProductos = false;
      }
    },

    // ⇨ se dispara al cambiar alimento
    onProductoChange() {
      const num = Number(this.productoSeleccionado);
      this.productoSeleccionado = Number.isFinite(num) ? num : null;

      // reset de lotes
      this.lotes = [];
      this.loteSeleccionado = '';

      if (this.productoSeleccionado) {
        this.cargarLotesDeProducto(this.productoSeleccionado);
      }
    },

    async cargarLotesDeProducto(productoId) {
      this.cargandoLotes = true;
      try {
        const { data } = await api.get('/entradaunitaria/', {
          params: { producto_id: Number(productoId) },
        });
        const filas = Array.isArray(data) ? data : [];
        this.lotes = filas
          .filter(eu => (eu?.lote ?? '').toString().trim() !== '')
          .map((eu, i) => ({
            id: eu.id ?? eu.id_entradaunitaria ?? `${productoId}-${eu.lote}-${i}`,
            etiqueta: eu.lote,
          }));
      } catch (e) {
        console.error('Error cargando lotes:', e);
        this.lotes = [];
      } finally {
        this.cargandoLotes = false;
      }
    },

    async submitForm() {
      if (!this.productoSeleccionado) return alert('Seleccione un alimento.');
      if (!this.loteSeleccionado) return alert('Seleccione un lote.');
      if (this.registro.kg == null || this.registro.kg < 0) return alert('Ingrese kg válidos.');

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
