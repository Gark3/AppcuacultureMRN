<template>
  <div class="cuarentena">
    <h1>Registrar Cuarentena</h1>

    <form @submit.prevent="registrarCuarentena">
      <!-- Selección de Estanque -->
      <div class="form-group">
        <label for="estanque">Selecciona el estanque:</label>
        <select v-model="cuarentena.estanque" id="estanque" required>
          <option v-for="estanque in estanques" :key="estanque.id" :value="estanque.id">
            {{ estanque.nombre }}
          </option>
        </select>
      </div>

      <!-- Motivo de Cuarentena -->
      <div class="form-group">
        <label for="motivo">Motivo de la cuarentena:</label>
        <input type="text" id="motivo" v-model="cuarentena.motivo" required />
      </div>

      <!-- Descripción de lo sucedido -->
      <div class="form-group">
        <label for="descripcion">Descripción de lo sucedido:</label>
        <textarea id="descripcion" v-model="cuarentena.descripcion" required></textarea>
      </div>

      <!-- Botón de Registro -->
      <button type="submit" class="btn-registrar" :disabled="loading">
        {{ loading ? 'Registrando...' : 'Registrar Cuarentena' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";

export default {
  setup() {
    const estanques = ref([]);
    const loading = ref(false);

    const cuarentena = reactive({
      estanque: "",
      motivo: "",
      descripcion: ""
    });

    const fetchEstanques = async () => {
      try {
        // Simulación de carga de estanques
        await new Promise(resolve => setTimeout(resolve, 1000));
        estanques.value = [
          { id: 1, nombre: "Estanque 1" },
          { id: 2, nombre: "Estanque 2" },
          { id: 3, nombre: "Estanque 3" }
        ];
      } catch (error) {
        console.error("Error al cargar estanques", error);
      }
    };

    const registrarCuarentena = async () => {
      if (!cuarentena.estanque || !cuarentena.motivo || !cuarentena.descripcion) {
        alert("Por favor, complete todos los campos.");
        return;
      }
      loading.value = true;
      try {
        console.log("Registrando cuarentena:", cuarentena);
        await new Promise(resolve => setTimeout(resolve, 2000));
        alert("Cuarentena registrada exitosamente");
      } catch (error) {
        alert("Error al registrar cuarentena");
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchEstanques);

    return { estanques, cuarentena, registrarCuarentena, loading };
  }
};
</script>

<style scoped>
.cuarentena {
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
