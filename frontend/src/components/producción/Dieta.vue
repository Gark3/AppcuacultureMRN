<template>
  <div class="dieta">
    <h1>Registrar Dieta</h1>

    <form @submit.prevent="registrarDieta">
      <!-- Selección de Alimento -->
      <div class="form-group">
        <label for="alimento">Selecciona el alimento:</label>
        <select v-model="dieta.alimento" id="alimento" required>
          <option v-for="alimento in alimentos" :key="alimento" :value="alimento">
            {{ alimento }}
          </option>
        </select>
      </div>

      <!-- Biomasa estimada (no editable) -->
      <div class="form-group">
        <label for="biomasa">Biomasa estimada (kg):</label>
        <input type="number" id="biomasa" :value="biomasaCalculada" disabled />
      </div>

      <!-- Kg diarios -->
      <div class="form-group">
        <label for="kgdiario">Kg diarios:</label>
        <input type="number" id="kgdiario" v-model.number="dieta.kgDiarios" step="0.01" required />
      </div>

      <!-- Peso Meta -->
      <div class="form-group">
        <label for="peso-meta">Peso meta por organismo (g):</label>
        <input type="number" id="peso-meta" v-model.number="dieta.pesoMeta" required min="1" step="0.1" />
      </div>

      <!-- Tiempo Estimado -->
      <div class="form-group">
        <label for="tiempo">Tiempo estimado (días):</label>
        <input type="number" id="tiempo" v-model.number="dieta.tiempoEstimado" required min="1" />
      </div>

      <!-- Frecuencia de Alimentación -->
      <div class="form-group">
        <label for="frecuencia">Frecuencia de alimentación diaria:</label>
        <select v-model="dieta.frecuencia" id="frecuencia" required>
          <option>1</option>
          <option>2</option>
          <option>3</option>
        </select>
      </div>

      <!-- Notas Adicionales -->
      <div class="form-group">
        <label for="notas">Notas adicionales:</label>
        <textarea id="notas" v-model="dieta.notas"></textarea>
      </div>

      <!-- Botón de Registro -->
      <button type="submit" class="btn-registrar" :disabled="loading">
        {{ loading ? 'Registrando...' : 'Registrar Dieta' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";
import axios from '@/services/axios';

export default {
  props: ['id'], // ID de la siembra
  setup(props) {
    const alimentos = ref(["Pellet", "Harina de pescado", "Algas", "Alimento balanceados"]);
    const loading = ref(false);
    const biomasaCalculada = ref(0);

    const dieta = reactive({
      alimento: "",
      pesoMeta: null,
      tiempoEstimado: null,
      frecuencia: "",
      notas: "",
      kgDiarios: null,
      siembra: props.id,
      usuario: null,
      acuicola: null,
      estado: 1
    });

    const calcularBiomasa = async () => {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        dieta.usuario = user.usuario_id;
        dieta.acuicola = user.acuicola;

        const [siembraRes, alimentarRes, crecimientoRes] = await Promise.all([
          axios.get(`/siembra/${props.id}/`),
          axios.get('/alimentar/'),
          axios.get('/crecimiento/')
        ]);

        const siembra = siembraRes.data;
        const totalSembrado = Number(siembra.cantidad_organismos || 0);
        const pesoInicial = Number(siembra.peso_promedio || 0);

        const mortalidades = alimentarRes.data
          .filter(a => a.siembra === siembra.id_siembra)
          .reduce((acc, cur) => acc + (Number(cur.mortalidad) || 0), 0);

        const sobrevivientes = totalSembrado - mortalidades;

        let pesoPromedio = pesoInicial;
        const crecimientoHoy = crecimientoRes.data
          .filter(c => c.siembra === siembra.id_siembra);

        if (crecimientoHoy.length > 0) {
          const fechas = [...new Set(crecimientoHoy.map(c => c.fecha))];
          const ultimaFecha = fechas.sort().pop();

          const pesos = crecimientoHoy
            .filter(c => c.fecha === ultimaFecha)
            .map(c => Number(c.gramos_organismo))
            .filter(p => !isNaN(p));

          if (pesos.length > 0) {
            const total = pesos.reduce((a, b) => a + b, 0);
            pesoPromedio = total / pesos.length;
          }
        }

        const biomasa = (sobrevivientes > 0 && pesoPromedio > 0)
          ? ((sobrevivientes * pesoPromedio) / 1000).toFixed(2)
          : 0;

        biomasaCalculada.value = biomasa;

      } catch (err) {
        console.error("Error al calcular biomasa estimada:", err);
        biomasaCalculada.value = 0;
      }
    };

    const registrarDieta = async () => {
      if (!dieta.alimento || !dieta.pesoMeta || !dieta.tiempoEstimado || !dieta.frecuencia || !dieta.kgDiarios) {
        alert("Por favor, complete todos los campos.");
        return;
      }
      loading.value = true;
      try {
        await axios.post('/dieta/', dieta);
        alert("Dieta registrada exitosamente");
      } catch (error) {
        alert("Error al registrar la dieta");
      } finally {
        loading.value = false;
      }
    };

    onMounted(calcularBiomasa);

    return { alimentos, dieta, registrarDieta, loading, biomasaCalculada };
  }
};
</script>


<style scoped>
.dieta {
  font-family: 'Poppins', sans-serif;
    max-width: auto;
    margin: 30px auto;
    padding: 25px;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease-in-out;
  }

  .registro-siembra:hover {
    box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.15);
  }

  h1 {
    text-align: center;
    color: #333;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
  }

  .form-group {
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
  }

  label {
    font-weight: 600;
    margin-bottom: 8px;
    color: #444;
    font-size: 14px;
  }

  input, select {
    width: 100%;
    padding: 12px;
    box-sizing: border-box;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.3s ease-in-out;
    background: #f8f9fa;
  }

  input:focus, select:focus {
    border-color: #28a745;
    outline: none;
    box-shadow: 0px 0px 5px rgba(40, 167, 69, 0.4);
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
    display: flex;
    align-items: center;
    justify-content: center;
  }

  button:hover {
    background-color: #218838;
    transform: scale(1.05);
  }

  button:active {
    transform: scale(0.98);
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .registro-siembra {
      padding: 20px;
    }

    h1 {
      font-size: 20px;
    }

    button {
      font-size: 14px;
      padding: 10px;
    }
  }
</style>
