<template>
  <div class="tratamientos">
    <h1>Registrar Tratamiento</h1>

    <form @submit.prevent="registrarTratamiento">
      <!-- Motivo del Tratamiento -->
      <div class="form-group">
        <label for="motivo">Motivo del tratamiento:</label>
        <input type="text" id="motivo" v-model="tratamiento.motivo" required />
      </div>

      <!-- Tratamiento Aplicado -->
      <div class="form-group">
        <label for="tipo">Tratamiento aplicado:</label>
        <input type="text" id="tipo" v-model="tratamiento.tipo" required />
      </div>

      <!-- Cantidad Suministrada -->
      <div class="form-group">
        <label for="cantidad">Cantidad suministrada (ml/g):</label>
        <input type="number" id="cantidad" v-model.number="tratamiento.cantidad" required min="1" step="0.1" />
      </div>

      <!-- Frecuencia del Tratamiento -->
      <div class="form-group">
        <label for="frecuencia">Frecuencia de aplicación:</label>
        <select v-model="tratamiento.frecuencia" id="frecuencia" required>
          <option>Diaria</option>
          <option>Semanal</option>
          <option>Mensual</option>
        </select>
      </div>

      <!-- Observaciones -->
      <div class="form-group">
        <label for="observacion">Observaciones:</label>
        <textarea id="observacion" v-model="tratamiento.observacion"></textarea>
      </div>

      <button type="submit" class="btn-registrar" :disabled="loading">
        {{ loading ? 'Registrando...' : 'Registrar Tratamiento' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "@/services/axios";

export default {
  name: "Tratamientos",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const loading = ref(false);

    const tratamiento = reactive({
      motivo: "",
      tipo: "",
      cantidad: null,
      frecuencia: "",
      observacion: "",
      estado: 1,
      siembra: null,
      usuario: null,
      acuicola: null,
    });

    onMounted(() => {
      const user = JSON.parse(localStorage.getItem("user"));
      tratamiento.siembra = parseInt(route.params.id);
      tratamiento.usuario = user?.usuario_id;
      tratamiento.acuicola = user?.acuicola;
    });

    const registrarTratamiento = async () => {
      console.log("Tratamiento a registrar:", tratamiento);
      if (
          tratamiento.motivo.trim() === "" ||
          tratamiento.tipo.trim() === "" ||
          tratamiento.frecuencia.trim() === "" ||
          tratamiento.observacion.trim() === "" ||
          tratamiento.cantidad === null ||
          isNaN(tratamiento.cantidad)
        ) {
          alert("Por favor, complete todos los campos.");
          return;
        }

      try {
        loading.value = true;
        await axios.post("/tratamiento/", tratamiento);
        alert("Tratamiento registrado exitosamente.");
        router.push("/producción/tratamientos"); // Redirecciona
      } catch (error) {
        console.error("Error al registrar tratamiento:", error.response?.data || error);
        alert("Error al registrar tratamiento.");
      } finally {
        loading.value = false;
      }
    };

    return {
      tratamiento,
      registrarTratamiento,
      loading,
    };
  },
};
</script>


<style scoped>
.tratamientos {
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
