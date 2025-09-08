<template>
  <div class="traslado">
    <h1>Registrar Transferencia</h1>

    <form @submit.prevent="registrarTraslado">
      <!-- Selección de Estanque Origen -->
      <div class="form-group">
        <label for="estanque-origen">Selecciona el estanque de origen:</label>
        <select v-model="traslado.origen" id="estanque-origen" required>
          <option v-for="estanque in estanquesEnUso" :key="estanque.id" :value="estanque.id">
            {{ estanque.nombre }}
          </option>
        </select>
      </div>

      <!-- Selección de Estanque Destino -->
      <div class="form-group">
        <label for="estanque-destino">Selecciona el estanque de destino:</label>
        <select v-model="traslado.destino" id="estanque-destino" required>
          <option v-for="estanque in estanquesDisponibles" :key="estanque.id" :value="estanque.id">
            {{ estanque.nombre }}
          </option>
        </select>
      </div>

      <!-- Tipo de Traslado -->
      <div class="form-group">
        <label>Tipo de traslado:</label>
        <div class="radio-group">
          <label>
            <input type="radio" id="total" value="total" v-model="traslado.tipo" required />
            Total
          </label>
          <label>
            <input type="radio" id="parcial" value="parcial" v-model="traslado.tipo" required />
            Parcial
          </label>
        </div>
      </div>

      <!-- Número de Organismos (Solo si es traslado parcial) -->
      <div class="form-group" v-if="traslado.tipo === 'parcial'">
        <label for="cantidad">Número de organismos a trasladar:</label>
        <input type="number" id="cantidad" v-model.number="traslado.cantidad" required min="1" />
      </div>

      <!-- Botón de Registro -->
      <button type="submit" class="btn-registrar" :disabled="loading">
        {{ loading ? 'Registrando...' : 'Registrar Traslado' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";

export default {
  setup() {
    const estanquesEnUso = ref([]);
    const estanquesDisponibles = ref([]);
    const loading = ref(false);

    const traslado = reactive({
      origen: "",
      destino: "",
      tipo: "",
      cantidad: null
    });

    const fetchEstanques = async () => {
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        estanquesEnUso.value = [
          { id: 1, nombre: "Estanque A" },
          { id: 2, nombre: "Estanque B" }
        ];
        estanquesDisponibles.value = [
          { id: 3, nombre: "Estanque C" },
          { id: 4, nombre: "Estanque D" }
        ];
      } catch (error) {
        console.error("Error al cargar estanques", error);
      }
    };

    const registrarTraslado = async () => {
      if (!traslado.origen || !traslado.destino || !traslado.tipo || (traslado.tipo === 'parcial' && !traslado.cantidad)) {
        alert("Por favor, complete todos los campos.");
        return;
      }
      loading.value = true;
      try {
        console.log("Registrando traslado:", traslado);
        await new Promise(resolve => setTimeout(resolve, 2000));
        alert("Traslado registrado exitosamente");
      } catch (error) {
        alert("Error al registrar el traslado");
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchEstanques);

    return { estanquesEnUso, estanquesDisponibles, traslado, registrarTraslado, loading };
  }
};
</script>

<style scoped>
.traslado {
  font-family: 'Poppins', sans-serif;
  max-width: auto;
  margin: 30px auto;
  padding: 25px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}

.traslado:hover {
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

.radio-group {
  display: flex;
  gap: 15px;
  align-items: center;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
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

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
  .traslado {
    padding: 20px;
  }

  h1 {
    font-size: 20px;
  }

  button {
    font-size: 14px;
    padding: 10px;
  }

  .radio-group {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
