<template>
  <div class="registro-siembra">
    <h1>Alimentación</h1>

    <form @submit.prevent="submitForm">
      <!-- Producto / Alimento -->
      <div class="form-group">
        <label for="productoId">Alimento</label>
        <select
          id="productoId"
          v-model.number="productoSeleccionado"
          :disabled="cargandoProductos"
          required
        >
          <option value="" disabled>
            {{ cargandoProductos ? 'Cargando…' : 'Seleccione un alimento' }}
          </option>

          <option
            v-for="p in productosAlimento"
            :key="getProductoId(p)"
            :value="getProductoId(p)"
          >
            {{ p.nombre }}
            <template v-if="p.presentacion"> · {{ p.presentacion }}</template>
            <template v-if="p.porcentaje_proteina"> · {{ p.porcentaje_proteina }}% proteína</template>
          </option>
        </select>

        <small v-if="!cargandoProductos && productosAlimento.length === 0" class="text-muted">
          No hay productos del rubro “Alimento”.
        </small>
      </div>

      <!-- Lote (según producto) -->
      <div class="form-group">
        <label for="lote">Lote</label>
        <select
          id="lote"
          v-model="loteSeleccionado"
          :disabled="!productoSeleccionado || cargandoLotes"
          required
        >
          <option value="" disabled>
            {{ !productoSeleccionado ? 'Seleccione un alimento primero'
               : (cargandoLotes ? 'Cargando lotes…' : 'Seleccione un lote') }}
          </option>

          <option v-for="l in lotes" :key="l.id" :value="l.id">
            {{ l.etiqueta }}
          </option>
        </select>

        <small v-if="productoSeleccionado && !cargandoLotes && lotes.length === 0" class="text-muted">
          Este alimento no tiene lotes disponibles.
        </small>
      </div>

      <!-- Cantidad -->
      <div class="form-group">
        <label for="kg">Cantidad de Alimento (kg)</label>
        <input
          type="number"
          id="kg"
          v-model="registro.kg"
          min="0"
          step="0.01"
          placeholder="Ingrese la cantidad de alimento"
          required
        />
      </div>

      <!-- Supervivencia -->
      <div class="form-group">
        <label for="supervivencia">Supervivencia</label>
        <input
          type="number"
          id="supervivencia"
          v-model="registro.supervivencia"
          min="0"
          step="0.01"
          placeholder="Ingrese la supervivencia"
        />
      </div>

      <!-- Clima -->
      <div class="form-group">
        <label for="clima">Clima</label>
        <input type="text" id="clima" v-model="registro.clima" placeholder="Ingrese el clima actual" />
      </div>

      <!-- Observación -->
      <div class="form-group">
        <label for="observacion">Comentarios</label>
        <textarea id="observacion" v-model="registro.observacion" placeholder="Ingrese algún comentario"></textarea>
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
  name: 'RegistroAlimentacion',
  props: ['id'], // id de siembra desde la ruta
  data() {
    return {
      // selección
      productoSeleccionado: null,
      loteSeleccionado: null,

      // catálogos
      productosAlimento: [],
      lotes: [],

      // ids auxiliares (por si rubro pasa a FK en el futuro)
      idRubroAlimento: null,

      // estados UI
      cargandoProductos: false,
      cargandoLotes: false,
      guardando: false,

      // payload extra
      registro: {
        kg: null,
        supervivencia: null,
        clima: '',
        observacion: '',
      },

      // siembra
      siembraId: null,
    };
  },

  watch: {
    // cuando cambia el producto, recarga lotes
    productoSeleccionado(nuevo) {
      this.loteSeleccionado = null;
      this.lotes = [];
      if (nuevo) this.cargarLotesDeProducto(nuevo);
    },
  },

  mounted() {
    this.siembraId = Number(this.id);
    this.cargarRubrosYProductos();
  },

  methods: {
    // --- helpers robustos
    getProductoId(p) {
      return p?.id ?? p?.id_producto ?? null;
    },
    esRubroAlimento(valor) {
      // soporta texto "Alimento" o id numérico (si mañana migras a FK)
      if (valor != null && isNaN(valor)) {
        return String(valor).trim().toLowerCase() === 'alimento';
      }
      return this.idRubroAlimento != null && Number(valor) === Number(this.idRubroAlimento);
    },

    // --- carga de catálogos
    async cargarRubrosYProductos() {
      this.cargandoProductos = true;
      try {
        const [rubrosRes, productosRes] = await Promise.all([
          api.get('/rubro/'),
          api.get('/producto/'),
        ]);

        // intenta detectar el id del rubro "Alimento" (por si luego es FK)
        const rubros = Array.isArray(rubrosRes.data) ? rubrosRes.data : [];
        this.idRubroAlimento =
          rubros.find(r => (r?.nombre || '').trim().toLowerCase() === 'alimento')?.id ?? null;

        // filtra productos que sean de rubro "Alimento"
        const productos = Array.isArray(productosRes.data) ? productosRes.data : [];
        this.productosAlimento = productos.filter(p =>
          this.esRubroAlimento(p?.rubro ?? p?.rubro_id)
        );
      } catch (e) {
        console.error('Error cargando rubros/productos:', e);
        this.productosAlimento = [];
      } finally {
        this.cargandoProductos = false;
      }
    },

    async cargarLotesDeProducto(productoId) {
      this.cargandoLotes = true;
      try {
        // Ajusta el nombre del parámetro si tu viewset usa otro (producto_id, etc.)
        const { data } = await api.get('/entradaunitaria/', { params: { producto: productoId } });
        const filas = Array.isArray(data) ? data : [];

        // Normaliza etiqueta para mostrar info útil
        this.lotes = filas.map((eu) => {
          const etiqueta = [
            eu.lote ? `Lote: ${eu.lote}` : null,
            eu.presentacion || null,
            (typeof eu.stock !== 'undefined') ? `stock: ${eu.stock}` : null,
          ].filter(Boolean).join(' · ') || `#${eu.id ?? eu.id_entradaunitaria ?? '—'}`;

          return {
            id: eu.id ?? eu.id_entradaunitaria ?? eu.pk,
            etiqueta,
          };
        });
      } catch (e) {
        console.error('Error cargando lotes:', e);
        this.lotes = [];
      } finally {
        this.cargandoLotes = false;
      }
    },

    // --- enviar
    async submitForm() {
      try {
        this.guardando = true;

        if (!this.siembraId) {
          alert('No se encontró el ciclo de siembra.');
          return;
        }
        if (!this.productoSeleccionado) {
          alert('Selecciona un alimento.');
          return;
        }
        if (!this.loteSeleccionado) {
          alert('Selecciona un lote.');
          return;
        }

        const payload = {
          siembra: this.siembraId,
          producto: this.productoSeleccionado, // id normalizado
          lote: this.loteSeleccionado,        // id de entrada unitaria/lote
          kg: this.registro.kg != null ? Number(this.registro.kg) : null,
          supervivencia: this.registro.supervivencia != null ? Number(this.registro.supervivencia) : null,
          clima: this.registro.clima ? String(this.registro.clima).trim() : '',
          observacion: this.registro.observacion ? String(this.registro.observacion).trim() : '',
          // estado: 1, // solo si tu modelo lo requiere explícitamente
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
.registro-siembra:hover { box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.15); }

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
  box-shadow: 0px 0px 5px rgba(40, 167, 69, 0.4);
}
.text-muted { color: #6b7280; font-size: 12px; margin-top: 4px; }

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
  display: flex;
  align-items: center;
  justify-content: center;
}
button:hover { background-color: #218838; transform: scale(1.05); }
button:active { transform: scale(0.98); }

@media (max-width: 768px) {
  .registro-siembra { padding: 20px; }
  h1 { font-size: 20px; }
  button { font-size: 14px; padding: 10px; }
}
</style>
