<template>
  <div class="adicion-organismos">
    <h1>Adición de Organismos</h1>

    <form @submit.prevent="agregarOrganismos">
      <!-- Selección de Siembra -->
      <div class="form-group">
        <label for="siembra">Selecciona la siembra:</label>
        <select v-model="adicion.siembra" id="siembra" required>
          <option v-for="siembra in siembras" :key="siembra.id" :value="siembra.id">
            {{ siembra.nombre }} ({{ siembra.especie }})
          </option>
        </select>
      </div>

      <!-- Número de Organismos -->
      <div class="form-group">
        <label for="numero-organismos">Número de organismos a agregar:</label>
        <input type="number" id="numero-organismos" v-model.number="adicion.numeroOrganismos" required min="1" />
      </div>

      <!-- Peso Promedio -->
      <div class="form-group">
        <label for="peso-promedio">Peso promedio por organismo (g):</label>
        <input type="number" id="peso-promedio" v-model.number="adicion.pesoPromedio" step="0.01" required min="0.1" />
      </div>

      <!-- Fecha de Adición -->
      <div class="form-group">
        <label for="fecha-adicion">Fecha de adición:</label>
        <input type="date" id="fecha-adicion" v-model="adicion.fecha" required />
      </div>

      <button type="submit" class="btn-agregar" :disabled="loading">
        {{ loading ? 'Agregando...' : 'Agregar Organismos' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";

export default {
  setup() {
    const siembras = ref([]);
    const loading = ref(false);

    const adicion = reactive({
      siembra: "",
      numeroOrganismos: null,
      pesoPromedio: null,
      fecha: ""
    });

    const fetchSiembras = async () => {
      try {
        // Simulación de carga de siembras
        await new Promise(resolve => setTimeout(resolve, 1000));
        siembras.value = [
          { id: 1, nombre: "Siembra Tilapia", especie: "Tilapia - Oreochromis niloticus" },
          { id: 2, nombre: "Siembra Camarón", especie: "Camarón blanco del Pacífico - Litopenaeus vannamei" }
        ];
      } catch (error) {
        console.error("Error al cargar siembras", error);
      }
    };

    const agregarOrganismos = async () => {
      if (!adicion.siembra || !adicion.numeroOrganismos || !adicion.pesoPromedio || !adicion.fecha) {
        alert("Por favor, complete todos los campos.");
        return;
      }
      loading.value = true;
      try {
        console.log("Agregando organismos:", adicion);
        await new Promise(resolve => setTimeout(resolve, 2000));
        alert("Organismos agregados exitosamente");
      } catch (error) {
        alert("Error al agregar organismos");
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchSiembras);

    return { siembras, adicion, agregarOrganismos, loading };
  }
};
</script>

<style scoped>
.adicion-organismos {
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
