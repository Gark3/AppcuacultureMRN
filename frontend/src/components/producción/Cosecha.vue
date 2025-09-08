<template>
  <div class="registro-siembra">
    <h1>Cosecha</h1>
    <form @submit.prevent="guardarCosecha">
      <!-- Datos Calculados -->
      <div class="form-group">
        <label for="numeroOrganismos">Número de organismos:</label>
        <input type="number" id="numeroOrganismos" v-model="datosCalculados.numeroOrganismos" readonly />
      </div>

      <div class="form-group">
        <label for="pesoPromedio">Peso promedio (gramos):</label>
        <input type="number" id="pesoPromedio" v-model="datosCalculados.pesoPromedio" readonly />
      </div>

      <div class="form-group">
        <label for="biomasaEstimada">Biomasa estimada (kg):</label>
        <input type="number" id="biomasaEstimada" v-model="datosCalculados.biomasaEstimada" readonly />
      </div>

      <!-- Datos Ingresados Manualmente -->
      <div class="form-group">
        <label for="biomasa_real">Biomasa real (kg):</label>
        <input type="number" id="biomasa_real" v-model.number="datosUsuario.biomasa_real" required />
      </div>

      <div class="form-group">
        <label for="destino">Destino:</label>
        <input type="text" id="destino" v-model="datosUsuario.destino" required />
      </div>

      <div class="form-group">
        <label for="documento">Documento:</label>
        <input type="text" id="documento" v-model="datosUsuario.documento" required />
      </div>

      <div class="form-group">
        <label for="transporte">Transportista:</label>
        <input type="text" id="transporte" v-model="datosUsuario.transporte" required />
      </div>

      <button type="submit">Guardar</button>
    </form>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "@/services/axios";
import { useRoute, useRouter } from "vue-router";

export default {
  name: "Cosecha",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const siembraId = route.params.id;
    const user = JSON.parse(localStorage.getItem("user"));

    const datosCalculados = ref({
      numeroOrganismos: 0,
      pesoPromedio: 0,
      biomasaEstimada: 0,
    });

    const datosUsuario = ref({
      biomasa_real: null,
      destino: "",
      documento: "",
      transporte: "",
    });

    const calcularDatos = async () => {
      try {
        const siembra = await axios.get(`/siembra/${siembraId}/`);
        const alimentar = await axios.get(`/alimentar/?siembra=${siembraId}`);
        const crecimiento = await axios.get(`/crecimiento/?siembra=${siembraId}`);

        const mortalidadTotal = alimentar.data.reduce((sum, a) => sum + (a.mortalidad || 0), 0);
        const organismosActuales = siembra.data.cantidad_organismos - mortalidadTotal;

        const fechasCrecimiento = [...new Set(crecimiento.data.map(c => c.fecha))];
        const ultimaFecha = fechasCrecimiento.sort().pop();
        const ultimosCrecimientos = crecimiento.data.filter(c => c.fecha === ultimaFecha);
        const pesoPromedio = ultimosCrecimientos.length
          ? ultimosCrecimientos.reduce((sum, c) => sum + c.gramos_organismo, 0) / ultimosCrecimientos.length
          : siembra.data.peso_promedio;

        datosCalculados.value.numeroOrganismos = organismosActuales;
        datosCalculados.value.pesoPromedio = parseFloat(pesoPromedio.toFixed(2));
        datosCalculados.value.biomasaEstimada = parseFloat(((organismosActuales * pesoPromedio) / 1000).toFixed(2));
      } catch (error) {
        console.error("Error al calcular datos de cosecha:", error);
      }
    };

    const guardarCosecha = async () => {
      try {
        const payload = {
          ...datosUsuario.value,
          estado: 1,
          fecha: new Date().toISOString().split("T")[0],
          siembra: parseInt(siembraId),
          usuario: user.usuario_id,
          acuicola: user.acuicola,
        };

        await axios.post("/cosecha/", payload);
        await axios.patch(`/siembra/${siembraId}/`, { estado: 0 });
        

        alert("Cosecha registrada correctamente.");
        router.push("/producción/cosecha");
      } catch (error) {
        console.error("Error al guardar cosecha:", error);
        alert("Error al registrar la cosecha.");
      }
    };

    onMounted(calcularDatos);

    return {
      datosCalculados,
      datosUsuario,
      guardarCosecha,
    };
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
