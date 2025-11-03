<template>
  <div class="registro-siembra">
    <h1>Alimentación</h1>

    <form @submit.prevent="submitForm">
      <!-- Producto (Rubro: Alimento) -->
      <div class="form-group">
        <label for="producto">Alimento</label>
        <select
          id="producto"
          v-model.number="ui.productoId"
          @change="onProductoChange"
          required
        >
          <option :value="0" disabled>Seleccione un alimento</option>
          <option
            v-for="p in productos"
            :key="p.id"
            :value="p.id"
          >
            {{ p.nombre }}
          </option>
        </select>
        <small v-if="cargando.productos" class="text-muted">Cargando alimentos…</small>
        <small v-else-if="!productos.length" class="text-muted">
          No hay productos del rubro “Alimento”.
        </small>
      </div>

      <!-- Lote del producto -->
      <div class="form-group">
        <label for="lote">Lote</label>
        <select
          id="lote"
          v-model="ui.loteCodigo"
          :disabled="!ui.productoId || cargando.lotes"
          required
        >
          <option value="" disabled>Seleccione un lote</option>
          <option
            v-for="l in lotes"
            :key="l._key"
            :value="l.codigo"
          >
            {{ l.codigo }} <!-- + info extra visible -->
            <template v-if="l.caducidad || l.stock !== null">
              — <span v-if="l.caducidad">Cad: {{ l.caducidad }}</span><span v-if="l.caducidad && l.stock !== null"> · </span><span v-if="l.stock !== null">Disp: {{ l.stock }}</span>
            </template>
          </option>
        </select>
        <small v-if="cargando.lotes" class="text-muted">Cargando lotes…</small>
        <small v-else-if="ui.productoId && !lotes.length" class="text-muted">
          Este alimento no tiene lotes disponibles.
        </small>
      </div>

      <!-- Cantidad -->
      <div class="form-group">
        <label for="kg">Cantidad de Alimento (kg)</label>
        <input
          type="number"
          id="kg"
          v-model.number="registro.kg"
          placeholder="Ingrese la cantidad de alimento"
          step="0.01"
          min="0"
          required
        />
      </div>

      <!-- Supervivencia -->
      <div class="form-group">
        <label for="supervivencia">Supervivencia (%)</label>
        <input
          type="number"
          id="supervivencia"
          v-model.number="registro.supervivencia"
          placeholder="Ingrese la supervivencia"
          min="0"
          max="100"
        />
      </div>

      <!-- Clima -->
      <div class="form-group">
        <label for="clima">Clima</label>
        <input type="text" id="clima" v-model.trim="registro.clima" placeholder="Ingrese el clima actual" />
      </div>

      <!-- Observación -->
      <div class="form-group">
        <label for="observacion">Comentarios</label>
        <textarea id="observacion" v-model.trim="registro.observacion" placeholder="Ingrese algún comentario"></textarea>
      </div>

      <button type="submit" :disabled="guardando || !puedeGuardar">
        {{ guardando ? "Guardando…" : "Registrar Alimentación" }}
      </button>
    </form>
  </div>
</template>

<script>
import api from '@/services/axios';

export default {
  name: 'AlimentarRegistro',
  props: ['id'], // id de la siembra desde la ruta
  data() {
    return {
      // UI/control
      ui: {
        productoId: 0,
        loteCodigo: '', // guardamos el código de lote que verá el usuario
      },
      cargando: { productos: false, lotes: false },

      // Datos cargados
      productos: [],   // [{id, nombre}]
      lotes: [],       // [{_key, codigo, caducidad?, stock?}]

      // Registro (mantengo tus campos)
      registro: {
        kg: null,
        supervivencia: null,
        clima: '',
        observacion: '',
      },

      siembraId: null,
      guardando: false,
    };
  },

  computed: {
    puedeGuardar() {
      return (
        this.siembraId &&
        this.ui.productoId > 0 &&
        this.ui.loteCodigo &&
        this.registro.kg !== null &&
        this.registro.kg >= 0
      );
    },
  },

  async mounted() {
    this.siembraId = Number(this.id);
    await this.cargarProductosAlimento();
  },

  methods: {
    // =========================
    //   CARGA DE PRODUCTOS
    // =========================
    async cargarProductosAlimento() {
      this.cargando.productos = true;
      try {
        // 1) Obtener rubro "Alimento"
        let rubroId = await this.buscarRubroAlimentoId();

        // 2) Obtener productos por rubro si hay id; fallback: traer todos y filtrar
        let productos = [];
        if (rubroId) {
          // intenta con query por rubro
          const tryUrls = [
            `/producto/?rubro=${rubroId}`,
            `/producto/?rubro_id=${rubroId}`,
            `/producto/`, // fallback total
          ];
          productos = await this._firstOk(tryUrls, (data) => Array.isArray(data) ? data : []);
          // si fue el fallback total, filtramos en cliente
          productos = productos.filter((p) => this._esProductoAlimento(p, rubroId));
        } else {
          // no encontramos rubro por API, traemos todos y filtramos por nombre del rubro
          const { data } = await api.get('/producto/');
          productos = (Array.isArray(data) ? data : []).filter((p) => this._esProductoAlimentoPorNombre(p));
        }

        // Normalizamos a {id, nombre}
        this.productos = productos.map((p) => ({
          id: this._getId(p),
          nombre: p?.nombre ?? p?.name ?? `Producto #${this._getId(p) ?? '?'}`,
          _raw: p,
        })).filter((p) => p.id); // descarta si no tiene id

      } catch (e) {
        console.error('Error al cargar productos:', e);
        this.productos = [];
      } finally {
        this.cargando.productos = false;
      }
    },

    async buscarRubroAlimentoId() {
      try {
        // intentos de búsqueda de rubro por nombre
        const tryUrls = [
          '/rubro/?search=Alimento',
          '/rubro/?nombre=Alimento',
          '/rubro/', // fallback total
        ];
        const lista = await this._firstOk(tryUrls, (data) => Array.isArray(data) ? data : []);
        // Buscar por nombre (case-insensitive)
        const rubro = lista.find((r) =>
          String(r?.nombre ?? r?.name ?? '').trim().toLowerCase() === 'alimento'
        );
        return this._getId(rubro) || null;
      } catch (e) {
        console.warn('No se pudo resolver rubro "Alimento":', e?.message);
        return null;
      }
    },

    _esProductoAlimento(p, rubroId) {
      // Soporta producto.rubro == id o {id, nombre}
      const r = p?.rubro ?? p?.rubro_id;
      if (typeof r === 'number') return r === rubroId;
      if (typeof r === 'object' && r) return this._getId(r) === rubroId;
      return false;
    },

    _esProductoAlimentoPorNombre(p) {
      const r = p?.rubro ?? p?.rubro_id;
      const nombre = (typeof r === 'object' ? (r?.nombre ?? r?.name) : null);
      return String(nombre || '').trim().toLowerCase() === 'alimento';
    },

    _getId(obj) {
      if (!obj) return null;
      return obj.id ?? obj.id_producto ?? obj.id_estanque ?? obj.pk ?? null;
    },

    async _firstOk(urls, pick) {
      for (const u of urls) {
        try {
          const { data } = await api.get(u);
          return pick(data);
        } catch (_) {/* siguiente intento */}
      }
      return [];
    },

    // =========================
    //   CARGA DE LOTES
    // =========================
    async onProductoChange() {
      this.ui.loteCodigo = '';
      this.lotes = [];
      const pid = this.ui.productoId;
      if (!pid) return;

      this.cargando.lotes = true;
      try {
        // Intentamos con EntradaUnitaria (o el recurso donde llevas inventario por lote)
        // 1) Primero intentamos filtrar por disponible=1
        let lista = await this._firstOk(
          [
            `/entradaunitaria/?producto=${pid}&disponible=1`,
            `/entradaunitaria/?producto_id=${pid}&disponible=1`,
            `/entradaunitaria/?producto=${pid}`, // sin filtro, por si tu API no lo soporta
            `/entradaunitaria/?producto_id=${pid}`,
            `/entradaunitaria/`, // súper fallback
          ],
          (data) => Array.isArray(data) ? data : []
        );

        // Si trajimos todas, filtramos en cliente por producto
        if (lista.length && !lista.some((x) => (x?.producto === pid) || (x?.producto_id === pid) || (this._getId(x?.producto) === pid))) {
          lista = lista.filter((x) =>
            (x?.producto === pid) || (x?.producto_id === pid) || (this._getId(x?.producto) === pid)
          );
        }

        // Mapeo defensivo de campos típicos: lote, caducidad, stock/existencias/restante
        this.lotes = lista.map((x, idx) => {
          const codigo = String(x?.lote ?? x?.codigo_lote ?? x?.lote_numero ?? `LOTE-${idx + 1}`);
          const cad = x?.caducidad ?? x?.fecha_caducidad ?? x?.vencimiento ?? null;
          const stock = this._firstNumber(x?.stock, x?.existencias, x?.cantidad_disponible, x?.restante, null);
          return {
            _key: `${codigo}-${idx}`,
            codigo,
            caducidad: cad ? String(cad).slice(0, 10) : null,
            stock: (typeof stock === 'number' ? stock : null),
            _raw: x,
          };
        });

      } catch (e) {
        console.error('Error al cargar lotes:', e);
        this.lotes = [];
      } finally {
        this.cargando.lotes = false;
      }
    },

    _firstNumber(...vals) {
      for (const v of vals) {
        const n = Number(v);
        if (!Number.isNaN(n)) return n;
      }
      return null;
    },

    // =========================
    //   SUBMIT
    // =========================
    async submitForm() {
      try {
        this.guardando = true;

        if (!this.puedeGuardar) {
          alert('Complete producto, lote y cantidad.');
          return;
        }

        // Buscar el nombre del producto para compatibilidad con tu campo "tipo"
        const prod = this.productos.find((p) => p.id === this.ui.productoId);
        const nombreProducto = prod?.nombre ?? '';

        // Payload CONSERVANDO tu contrato actual:
        // - tipo: nombre del producto seleccionado (compatibilidad)
        // - lote: código/nombre del lote seleccionado
        // - kg, supervivencia, clima, observacion, siembra
        const payload = {
          tipo: nombreProducto,                          // <— compat
          lote: this.ui.loteCodigo,                      // <— compat (código de lote)
          kg: this.registro.kg != null ? Number(this.registro.kg) : null,
          supervivencia: this.registro.supervivencia != null ? Number(this.registro.supervivencia) : null,
          clima: this.registro.clima || '',
          observacion: this.registro.observacion || '',
          siembra: this.siembraId,                       // numérico
          // Si en el futuro migras el back: puedes enviar también producto_id/lote_id
          // producto: this.ui.productoId,
          // lote_id: (this.lotes.find(l => l.codigo===this.ui.loteCodigo)?._raw?.id ?? null),
        };

        await api.post('/alimentar/', payload);

        alert('¡Registro de alimentación guardado exitosamente!');
        this.$router.push('/producción/alimentar');
      } catch (error) {
        console.error('Error al registrar alimentación:', error);
        const msg = error?.response?.data?.detail || 'Ocurrió un error al guardar.';
        alert(msg);
      } finally {
        this.guardando = false;
      }
    },
  },
};
</script>

<style scoped>
.registro-siembra {
  font-family: 'Poppins', sans-serif;
  max-width: auto;
  margin: 30px auto;
  padding: 25px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}
.registro-siembra:hover { box-shadow: 0px 6px 15px rgba(0,0,0,0.15); }

h1 {
  text-align: center;
  color: #333;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
}
.form-group { margin-bottom: 20px; display: flex; flex-direction: column; }
label { font-weight: 600; margin-bottom: 8px; color: #444; font-size: 14px; }

input, select, textarea {
  width: 100%;
  padding: 12px;
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease-in-out;
  background: #f8f9fa;
}
input:focus, select:focus, textarea:focus {
  border-color: #28a745;
  outline: none;
  box-shadow: 0 0 5px rgba(40,167,69,0.4);
}

button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 12px 15px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease-in-out;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex; align-items: center; justify-content: center;
}
button:hover { background-color: #218838; transform: scale(1.05); }
button:active { transform: scale(0.98); }

/* Responsive */
@media (max-width: 768px) {
  .registro-siembra { padding: 20px; }
  h1 { font-size: 20px; }
  button { font-size: 14px; padding: 10px; }
}
.text-muted { color: #6b7280; }
</style>
