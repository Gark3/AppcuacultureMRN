<template>
  <div class="contenedor-costos">
    <h2>Costos Operativos</h2>

    <form @submit.prevent="registrarGasto" class="formulario">
      <label>Tipo de Gasto:
        <select v-model="nuevoGasto.tipo" required>
          <option disabled value="">Seleccione</option>
          <option v-for="tipo in tiposGasto" :key="tipo.id" :value="tipo.id">
            {{ tipo.nombre }}
          </option>
        </select>
      </label>

      <label>Descripción:
        <textarea v-model="nuevoGasto.descripcion" required></textarea>
      </label>

      <label>Monto:
        <input type="number" v-model.number="nuevoGasto.monto" step="0.01" required />
      </label>

      <label>
        <input type="checkbox" v-model="nuevoGasto.es_general" />
        Gasto general (para toda la granja)
      </label>

      <label v-if="!nuevoGasto.es_general">Ciclo de Siembra:
        <select v-model="nuevoGasto.siembra" required>
          <option disabled value="">Seleccione un ciclo</option>
          <option v-for="ciclo in ciclosActivos" :key="ciclo.id_siembra" :value="ciclo.id_siembra">
            Estanque {{ ciclo.estanque_nombre }} - {{ ciclo.etapa }}
          </option>
        </select>
      </label>

      <button type="submit">Registrar Gasto</button>
    </form>

    <hr />

    <h3>Historial de Gastos</h3>
    <div v-if="gastos.length === 0">
      <p>No hay gastos registrados.</p>
    </div>

    <div class="lista-gastos">
      <div v-for="gasto in gastos" :key="gasto.id" class="tarjeta">
        <h4>{{ gasto.tipo_nombre }}</h4>
        <p><strong>Monto:</strong> ${{ parseFloat(gasto.monto).toFixed(2) }}</p>
        <p><strong>Descripción:</strong> {{ gasto.descripcion }}</p>
        <p><strong>Fecha:</strong> {{ gasto.fecha }}</p>
        <p><strong>Tipo:</strong> {{ gasto.es_general ? 'General' : 'Específico' }}</p>
        <p v-if="!gasto.es_general"><strong>Ciclo:</strong> ID {{ gasto.siembra }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CostosOperativos',
  data() {
    return {
      tiposGasto: [],
      ciclosActivos: [],
      gastos: [],
      nuevoGasto: {
        tipo: "",
        descripcion: "",
        monto: 0,
        es_general: false,
        siembra: null,
      },
    };
  },
  methods: {
    async obtenerDatos() {
      try {
        const [resTipos, resCiclos, resGastos] = await Promise.all([
          axios.get('/api/tipos-gasto/'),
          axios.get('/api/siembra/'),
          axios.get('/api/gastos/'),
        ]);

        this.tiposGasto = resTipos.data;
        this.ciclosActivos = resCiclos.data.filter(c => !c.fecha_cosecha); // Activos
        this.gastos = resGastos.data;
      } catch (error) {
        console.error("Error al cargar los datos:", error);
      }
    },
    async registrarGasto() {
      try {
        const payload = { ...this.nuevoGasto };
        if (payload.es_general) payload.siembra = null;

        await axios.post('/api/gastos/', payload);
        this.limpiarFormulario();
        this.obtenerDatos();
      } catch (error) {
        console.error("Error al registrar el gasto:", error);
      }
    },
    limpiarFormulario() {
      this.nuevoGasto = {
        tipo: "",
        descripcion: "",
        monto: 0,
        es_general: false,
        siembra: null,
      };
    }
  },
  mounted() {
    this.obtenerDatos();
  },
};
</script>

<style scoped>
.contenedor-costos {
  max-width: auto;
  margin: auto;
  padding: 20px;
}

.formulario {
  display: grid;
  gap: 15px;
  margin-bottom: 30px;
}

input[type="number"],
textarea,
select {
  width: 100%;
  padding: 5px;
  font-size: 1em;
}

button {
  padding: 10px;
  background-color: #3498db;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.lista-gastos {
  display: grid;
  gap: 15px;
}

.tarjeta {
  background-color: #f2f2f2;
  border: 1px solid #ccc;
  padding: 15px;
  border-radius: 5px;
}
</style>
