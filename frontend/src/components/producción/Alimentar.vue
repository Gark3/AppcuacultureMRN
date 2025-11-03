<template>
  <div class="registro-siembra">
    <h1>Alimentación</h1>

    <form @submit.prevent="submitForm">
      <!-- PRODUCTO (solo rubro = Alimento) -->
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
            :key="p.id"
            :value="p.id"
          >
            {{ p.nombre }}
            <template v-if="p.presentacion"> · {{ p.presentacion }}</template>
            <template v-if="p.porcentaje_proteina"> · {{ p.porcentaje_proteina }}% proteína</template>
          </option>
        </select>
        <small v-if="!cargandoProductos && productosAlimento.length===0" class="text-muted">
          No hay productos del rubro “Alimento”.
        </small>
      </div>

      <!-- LOTE del producto elegido -->
      <div class="form-group">
        <label for="loteId">Lote</label>
        <select
          id="loteId"
          v-model.number="loteSeleccionado"
          :disabled="!productoSeleccionado || cargandoLotes"
          required
        >
          <option value="" disabled>
            {{ !productoSeleccionado ? 'Seleccione primero un alimento' : (cargandoLotes ? 'Cargando lotes…' : 'Seleccione un lote') }}
          </option>
          <option v-for="l in lotes" :key="l.id" :value="l.id">
            {{ l.etiqueta }}
          </option>
        </select>
        <small v-if="productoSeleccionado && !cargandoLotes && lotes.length===0" class="text-muted">
          Este producto no tiene lotes disponibles.
        </small>
      </div>

      <!-- RESTO DE CAMPOS -->
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

      <div class="form-group">
        <label for="supervivencia">Supervivencia</label>
        <input type="number" id="supervivencia" v-model.number="registro.supervivencia" placeholder="Ingrese la supervivencia" />
      </div>

      <div class="form-group">
        <label for="clima">Clima</label>
        <input type="text" id="clima" v-model.trim="registro.clima" placeholder="Ingrese el clima actual" />
      </div>

      <div class="form-group">
        <label for="observacion">Comentarios</label>
        <textarea id="observacion" v-model.trim="registro.observacion" placeholder="Ingrese algún comentario"></textarea>
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
  name: 'AlimentacionRegistro',
  props: ['id'], // siembra_id desde la ruta
  data() {
    return {
      // control
      guardando: false,
      cargandoProductos: false,
      cargandoLotes: false,

      // ids y catálogos
      idRubroAlimento: null,
      productosAlimento: [],
      productoSeleccionado: null,

      lotes: [],
      loteSeleccionado: null,

      // payload
      registro: {
        kg: null,
        supervivencia: null,
        clima: '',
        observacion: '',
      },

      siembraId: null,
    };
  },

  mounted() {
    this.siembraId = Number(this.id);
    this.cargarRubrosYProductos();
  },

  watch: {
    // cuando cambia el producto, cargamos lotes
    productoSeleccionado(nuevo) {
      this.loteSeleccionado = null;
      this.lotes = [];
      if (!nuevo) return;
      this.cargarLotesDeProducto(nuevo);
    },
  },

  methods: {
    /** Opción B: buscar ID del rubro "Alimento" y filtrar los productos por ese ID */
    async cargarRubrosYProductos() {
      this.cargandoProductos = true;
      try {
        const [rubrosRes, productosRes] = await Promise.all([
          api.get('/rubro/'),
          api.get('/producto/'),
        ]);

        // 1) obtener id del rubro "Alimento"
        const rubros = Array.isArray(rubrosRes.data) ? rubrosRes.data : [];
        this.idRubroAlimento = rubros.find(
          r => (r.nombre || '').toLowerCase() === 'alimento'
        )?.id;

        // 2) filtrar productos por ese rubro
        const productos = Array.isArray(productosRes.data) ? productosRes.data : [];
        if (this.idRubroAlimento) {
          this.productosAlimento = productos.filter(p => Number(p.rubro) === Number(this.idRubroAlimento));
        } else {
          this.productosAlimento = [];
        }
      } catch (e) {
        console.error('Error cargando rubros/productos:', e);
        this.productosAlimento = [];
      } finally {
        this.cargandoProductos = false;
      }
    },

    /** Cargar lotes del producto elegido
     *  Ajusta este endpoint según tu modelo real de lotes.
     *  Aquí uso EntradaUnitaria como ejemplo y muestro etiqueta legible.
     */
    async cargarLotesDeProducto(productoId) {
      this.cargandoLotes = true;
      try {
        // Si usas filtros en DRF, esto te traerá solo las entradas del producto
        const { data } = await api.get(`/entradaunitaria/`, { params: { producto: productoId } });

        const filas = Array.isArray(data) ? data : [];
        // arma etiquetas amigables
        this.lotes = filas.map((eu) => {
          const etiquetaPartes = [];
          if (eu.lote) etiquetaPartes.push(`Lote: ${eu.lote}`);
          if (eu.presentacion) etiquetaPartes.push(`${eu.presentacion}`);
          if (typeof eu.stock !== 'undefined') etiquetaPartes.push(`stock: ${eu.stock}`);
          const etiqueta = etiquetaPartes.length ? etiquetaPartes.join(' · ') : `#${eu.id}`;
          return { id: eu.id, etiqueta };
        });
      } catch (e) {
        console.error('Error cargando lotes:', e);
        this.lotes = [];
      } finally {
        this.cargandoLotes = false;
      }
    },

    async submitForm() {
      try {
        this.guardando = true;

        // validaciones mínimas
        if (!this.siembraId) {
          alert('No se encontró el ciclo (siembra).');
          return;
        }
        if (!this.productoSeleccionado) {
          alert('Seleccione un alimento.');
          return;
        }
        if (!this.loteSeleccionado) {
          alert('Seleccione un lote.');
          return;
        }
        if (this.registro.kg == null || Number(this.registro.kg) <= 0) {
          alert('Ingrese la cantidad de alimento en kg.');
          return;
        }

        // payload para /alimentar/
        // (usuario y acuicola los setea el backend vía AcuicolaScopedMixin)
        const payload = {
          siembra: this.siembraId,
          producto: this.productoSeleccionado,
          lote: this.loteSeleccionado,       // ajusta clave si tu modelo usa otro nombre
          kg: Number(this.registro.kg),
          supervivencia: this.registro.supervivencia != null ? Number(this.registro.supervivencia) : null,
          clima: this.registro.clima || '',
          observacion: this.registro.observacion || '',
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

h1 { text-align: center; color: #333; font-size: 24px; font-weight: 600; margin-bottom: 20px; }

.form-group { margin-bottom: 20px; display: flex; flex-direction: column; }
label { font-weight: 600; margin-bottom: 8px; color: #444; font-size: 14px; }
.text-muted { color: #6b7280; font-size: 12px; }

input, select, textarea {
  width: 100%; padding: 12px; box-sizing: border-box;
  border: 1px solid #ddd; border-radius: 8px; font-size: 14px;
  transition: all 0.3s ease-in-out; background: #f8f9fa;
}
input:focus, select:focus, textarea:focus {
  border-color: #28a745; outline: none; box-shadow: 0 0 5px rgba(40,167,69,0.4);
}

button {
  background-color: #28a745; color: white; border: none; padding: 12px 15px;
  font-size: 16px; cursor: pointer; border-radius: 8px; font-weight: 600;
  transition: all 0.3s ease-in-out; text-transform: uppercase; letter-spacing: 1px;
  display: flex; align-items: center; justify-content: center;
}
button:hover { background-color: #218838; transform: scale(1.05); }
button:active { transform: scale(0.98); }

@media (max-width: 768px) {
  .registro-siembra { padding: 20px; }
  h1 { font-size: 20px; }
  button { font-size: 14px; padding: 10px; }
}
</style>
