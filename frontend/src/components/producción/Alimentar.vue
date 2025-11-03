<template>
  <section class="card">
    <div class="card__header">
      <h2 class="card__title">Alimentación</h2>
      <p class="card__sub">Registra alimento, lote y cantidad para la siembra seleccionada.</p>
    </div>

    <form class="form" @submit.prevent="submitForm">
      <!-- PRODUCTO (rubro Alimento) -->
      <div class="field">
        <label for="alimento">Alimento</label>
        <select
          id="alimento"
          class="input"
          v-model="productoSeleccionado"
          @change="onProductoChange"
          :disabled="cargandoProductos"
          required
        >
          <option value="" disabled>
            {{ cargandoProductos ? 'Cargando alimentos…' : 'Seleccione un alimento' }}
          </option>
          <option
            v-for="p in alimentos"
            :key="p.id"
            :value="p.id"
          >
            {{ formateaProducto(p) }}
          </option>
        </select>
        <small v-if="!alimentos.length && !cargandoProductos" class="text-muted">
          No hay productos del rubro “Alimento”.
        </small>
      </div>

      <!-- LOTE -->
      <div class="field">
        <label for="lote">Lote</label>
        <select
          id="lote"
          class="input"
          v-model="registro.lote"
          :disabled="!productoSeleccionado || cargandoLotes || !lotes.length"
          required
        >
          <option value="" disabled>
            {{
              cargandoLotes
                ? 'Cargando lotes…'
                : (!productoSeleccionado
                    ? 'Seleccione un alimento primero'
                    : (!lotes.length ? 'No hay lotes para este alimento' : 'Seleccione un lote'))
            }}
          </option>
          <option
            v-for="l in lotes"
            :key="l.value"
            :value="l.value"
          >{{ l.etiqueta }}</option>
        </select>
      </div>

      <!-- KG -->
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

      <!-- SUPERVIVENCIA -->
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

      <!-- CLIMA -->
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

      <!-- OBSERVACION -->
      <div class="field">
        <label for="obs">Comentarios (opcional)</label>
        <textarea
          id="obs"
          class="input"
          rows="3"
          v-model.trim="registro.observacion"
          placeholder="Notas u observaciones"
        ></textarea>
      </div>

      <div class="mt-2">
        <button class="btn btn--primary" type="submit" :disabled="guardando || !puedeEnviar">
          {{ guardando ? 'Guardando…' : 'Registrar Alimentación' }}
        </button>
      </div>
    </form>
  </section>
</template>

<script>
import api from '@/services/axios';

export default {
  name: 'RegistroAlimentacion',
  props: {
    id: { type: [String, Number], required: false }, // si viene por prop
  },
  data() {
    return {
      // catálogos
      alimentos: [],
      cargandoProductos: false,

      // lotes del producto seleccionado
      lotes: [],
      cargandoLotes: false,

      // selección
      productoSeleccionado: '',

      // form
      registro: {
        lote: '',
        kg: null,
        supervivencia: null,
        clima: '',
        observacion: '',
      },

      // misc
      guardando: false,
      siembraId: null,
    };
  },
  computed: {
    puedeEnviar() {
      return (
        this.productoSeleccionado &&
        this.registro.lote &&
        this.registro.kg > 0
      );
    },
  },
  methods: {
    // ---------- CARGA INICIAL ----------
    async cargarProductosAlimento() {
      this.cargandoProductos = true;
      try {
        // 1) Traer rubros para identificar "Alimento"
        const rubrosResp = await api.get('/rubro/');
        const rubros = Array.isArray(rubrosResp.data) ? rubrosResp.data : [];

        // Busca rubro "Alimento" (case-insensitive)
        const rubroAlimento = rubros.find(r =>
          String(r?.nombre ?? '').toLowerCase() === 'alimento'
        );

        // 2) Traer productos (scoped por acuícola en el back)
        const prodResp = await api.get('/producto/');
        const productos = Array.isArray(prodResp.data) ? prodResp.data : [];

        // 3) Filtrar por rubro "Alimento" de forma robusta
        const rubroId = rubroAlimento?.id ?? rubroAlimento?.id_rubro;
        this.alimentos = productos.filter(p => {
          const pr = p?.rubro;
          // puede venir número (id) o objeto
          const prId = typeof pr === 'number' ? pr : (pr?.id ?? pr?.id_rubro);
          const prNombre = typeof pr === 'string' ? pr : (pr?.nombre ?? '');
          const matchPorId = rubroId ? (prId === rubroId) : false;
          const matchPorNombre = String(prNombre).toLowerCase() === 'alimento';
          return matchPorId || matchPorNombre;
        });

        // Limpia selección si ya no existe el producto que estaba seleccionado
        if (this.productoSeleccionado && !this.alimentos.some(a => a.id === Number(this.productoSeleccionado))) {
          this.productoSeleccionado = '';
          this.lotes = [];
          this.registro.lote = '';
        }
      } catch (e) {
        console.error('Error cargando productos (rubro Alimento):', e);
        this.alimentos = [];
      } finally {
        this.cargandoProductos = false;
      }
    },

    // ---------- LOTES ----------
    async onProductoChange() {
      this.registro.lote = '';
      this.lotes = [];
      if (this.productoSeleccionado) {
        await this.cargarLotesDeProducto(this.productoSeleccionado);
      }
    },

    async cargarLotesDeProducto(productoId) {
      this.cargandoLotes = true;
      try {
        const { data } = await api.get('/entradaunitaria/', {
          params: { producto_id: Number(productoId) }, // <-- backend ya filtra así
        });

        const filas = Array.isArray(data) ? data : [];
        const vistos = new Set();
        this.lotes = filas
          .map(eu => (eu?.lote ?? '').toString().trim())
          .filter(l => l && !vistos.has(l) && (vistos.add(l), true))
          .map(l => ({ etiqueta: l, value: l }));

        // Autoseleccionar si solo hay un lote
        if (this.lotes.length === 1) {
          this.registro.lote = this.lotes[0].value;
        }
      } catch (err) {
        console.error('Error cargando lotes:', err);
        this.lotes = [];
      } finally {
        this.cargandoLotes = false;
      }
    },

    // ---------- FORMATO ----------
    formateaProducto(p) {
      const nombre = p?.nombre ?? '—';
      const prot = (p?.porcentaje_proteina ?? p?.proteina ?? '').toString().trim();
      const pres = (p?.presentacion ?? '').toString().trim();
      const partes = [nombre];
      if (prot) partes.push(`${prot}%`);
      if (pres) partes.push(pres);
      return partes.join(' · ');
    },

    // ---------- SUBMIT ----------
    async submitForm() {
      if (!this.puedeEnviar) return;
      this.guardando = true;
      try {
        const payload = {
          siembra: this.siembraId,                  // numérico
          producto: Number(this.productoSeleccionado), // id de producto
          lote: this.registro.lote,                 // string (ej. "00001")
          kg: this.registro.kg != null ? Number(this.registro.kg) : null,
          supervivencia: this.registro.supervivencia != null ? Number(this.registro.supervivencia) : null,
          clima: this.registro.clima || '',
          observacion: this.registro.observacion || '',
        };

        await api.post('/alimentar/', payload);

        alert('¡Registro de alimentación guardado exitosamente!');
        this.$router.push('/producción/alimentar'); // ajusta si tu ruta no usa acento
      } catch (e) {
        console.error('Error al registrar alimentación:', e);
        const msg = e?.response?.data?.detail || 'Ocurrió un error al guardar.';
        alert(msg);
      } finally {
        this.guardando = false;
      }
    },
  },

  mounted() {
    // siembra id puede llegar por prop o por ruta
    const rid = this.$route?.params?.id;
    this.siembraId = Number(this.id ?? rid);

    this.cargarProductosAlimento();
  },
};
</script>

<style scoped>
.form { margin-top: 8px; }
.field { margin-bottom: 14px; display: flex; flex-direction: column; }
label { font-weight: 600; margin-bottom: 6px; }
.input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #f8fafc;
  font-size: 14px;
}
.input:focus {
  outline: none;
  border-color: #7f1d1d;
  box-shadow: 0 0 0 2px rgba(127, 29, 29, 0.15);
}
.btn { padding: 10px 14px; border-radius: 10px; }
.btn--primary {
  background: #7f1d1d; color: #fff; border: none;
}
.btn--primary:disabled { opacity: .6; cursor: default; }
.text-muted { color: #6b7280; font-size: 12px; }
.mt-2 { margin-top: 12px; }
</style>
