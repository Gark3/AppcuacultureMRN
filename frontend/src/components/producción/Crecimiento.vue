<template>
  <div class="registro-siembra">
    <h1>Crecimiento</h1>
    <form @submit.prevent="guardarCrecimiento">
      <!-- Bloque Rubro: select siempre visible -->
      <div class="form-group">
        <label for="rubroSelect">Seleccionar Rubro:</label>
        <select id="rubroSelect" v-model="rubroSeleccionado">
          <option value="">Seleccione un rubro</option>
          <option v-for="rubro in rubros" :key="rubro.id_rubro" :value="rubro.id_rubro">
            {{ rubro.nombre }}
          </option>
        </select>
      </div>
      <!-- Botón para mostrar el formulario de agregar rubro -->
      <button type="button" class="btn-agregar" @click="mostrarAgregarRubro = !mostrarAgregarRubro">
        Agregar Rubro
      </button>
      <!-- Formulario para agregar rubro -->
      <div v-if="mostrarAgregarRubro" class="form-group">
        <label for="nuevoRubroNombre">Nombre del Rubro:</label>
        <input
          type="text"
          id="nuevoRubroNombre"
          v-model="nuevoRubro.nombre"
          placeholder="Nombre del rubro"
          required
        />
        <label for="nuevoRubroUnidad">Unidad de Medida:</label>
        <input
          type="text"
          id="nuevoRubroUnidad"
          v-model="nuevoRubro.unidad"
          placeholder="Unidad de medida"
          required
        />
        <button type="button" @click="agregarRubro">
          Agregar
        </button>
      </div>

      <!-- Resto del formulario existente -->
      <div class="form-group">
        <label for="cantidadOrganismos">Cantidad de organismos:</label>
        <input
          type="number"
          id="cantidadOrganismos"
          v-model.number="cantidadOrganismos"
          min="1"
          max="1000"
          placeholder="Ingresa la cantidad"
          @input="generarInputs"
        />
      </div>

      <div v-if="gramos_organismo.length > 0" class="form-group">
        <h3>Ingrese el peso del organismo (gramos):</h3>
        <div v-for="(peso, index) in gramos_organismo" :key="index" class="form-group">
          <label :for="'peso-' + (index + 1)">Organismo {{ index + 1 }}:</label>
          <input
            type="number"
            :id="'peso-' + (index + 1)"
            v-model.number="gramos_organismo[index]"
            min="0"
            step="0.01"
            placeholder="Peso en gramos"
            required
          />
        </div>
      </div>

      <button type="submit" :disabled="gramos_organismo.length === 0 || loading">
        {{ loading ? 'Guardando...' : 'Guardar' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from '@/services/axios';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: "Crecimiento",
  setup() {
    const route = useRoute();
    const router = useRouter();

    // Estado del formulario principal
    const cantidadOrganismos = ref(null);
    const gramos_organismo = ref([]);
    const loading = ref(false);

    // Estados para Rubro
    const rubros = ref([]);
    const rubroSeleccionado = ref("");
    const mostrarAgregarRubro = ref(false);
    const nuevoRubro = ref({
      nombre: "",
      unidad: ""
    });

    // Función para generar los inputs según la cantidad de organismos
    const generarInputs = () => {
      if (!cantidadOrganismos.value || cantidadOrganismos.value < 1 || cantidadOrganismos.value > 1000) {
        gramos_organismo.value = [];
        return;
      }
      gramos_organismo.value = Array.from({ length: cantidadOrganismos.value }, () => null);
    };

    // Función para guardar los registros de crecimiento
    const guardarCrecimiento = async () => {
      // Requerir que se haya seleccionado un rubro
      if (!rubroSeleccionado.value) {
        alert("Debe seleccionar un rubro.");
        return;
      }

      if (gramos_organismo.value.includes(null)) {
        alert("Por favor, complete todos los pesos antes de guardar.");
        return;
      }
      const user = JSON.parse(localStorage.getItem("user"));
      const siembraId = parseInt(route.params.id);
      const fechaActual = new Date().toISOString().split("T")[0]; // Formato YYYY-MM-DD
      
      // Convertir el valor del rubro a número
      const rubroId = parseInt(rubroSeleccionado.value);

      // Para cada organismo, se crea un registro de crecimiento
      const registros = gramos_organismo.value.map((gramos) => ({
        medicion: gramos,
        estado: 1,
        siembra: siembraId,
        usuario: user.usuario_id,
        acuicola: user.acuicola,
        fecha: fechaActual,
        rubro: rubroId
      }));

      try {
        loading.value = true;
        await Promise.all(registros.map((registro) => axios.post('/crecimiento/', registro)));
        alert("Registros de crecimiento guardados exitosamente.");
        router.push('/crecimiento');
      } catch (error) {
        console.error("Error al registrar crecimiento:", error.response?.data || error.message);
        alert("Ocurrió un error al guardar los datos.");
      } finally {
        loading.value = false;
      }
    };

    // Función para obtener rubros filtrados por acuícola (sin importar el usuario que los dio de alta)
    const obtenerRubros = async () => {
      try {
        const response = await axios.get('/rubro/');
        const user = JSON.parse(localStorage.getItem("user"));
        let rubrosFiltrados = response.data;
        if (Array.isArray(rubrosFiltrados)) {
          rubrosFiltrados = rubrosFiltrados.filter(rubro => {
            if (typeof rubro.acuicola === "object") {
              return rubro.acuicola.id_acuicola === user.acuicola;
            }
            return rubro.acuicola === user.acuicola;
          });
        }
        rubros.value = rubrosFiltrados;
      } catch (err) {
        console.error("Error al obtener rubros:", err);
      }
    };

    // Función para agregar un nuevo rubro
    const agregarRubro = async () => {
      const user = JSON.parse(localStorage.getItem("user"));
      if (!nuevoRubro.value.nombre || !nuevoRubro.value.unidad) {
        alert("Por favor, complete todos los campos para agregar el rubro.");
        return;
      }
      const payload = {
        nombre: nuevoRubro.value.nombre,
        unidad: nuevoRubro.value.unidad,
        usuario: user.usuario_id,
        acuicola: user.acuicola,
        estado: 1
      };
      try {
        const response = await axios.post('/rubro/', payload);
        alert("Rubro agregado exitosamente.");
        mostrarAgregarRubro.value = false;
        // Limpiar campos del formulario de rubro
        nuevoRubro.value.nombre = "";
        nuevoRubro.value.unidad = "";
        // Actualizar la lista de rubros
        await obtenerRubros();
        // Establecer el rubro recién agregado en el select (opcional)
        rubroSeleccionado.value = response.data.id_rubro || response.data.id;
      } catch (err) {
        console.error("Error al agregar rubro:", err.response?.data || err.message);
        alert("Ocurrió un error al agregar el rubro.");
      }
    };

    onMounted(() => {
      obtenerRubros();
    });

    return {
      cantidadOrganismos,
      gramos_organismo,
      generarInputs,
      guardarCrecimiento,
      loading,
      // Rubro
      rubros,
      rubroSeleccionado,
      mostrarAgregarRubro,
      nuevoRubro,
      obtenerRubros,
      agregarRubro
    };
  }
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
