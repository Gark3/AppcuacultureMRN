<template>
  <div class="registro-producto">
    <h1>Pago de Nómina</h1>

    <form @submit.prevent="guardarConfiguracion">
      <div class="form-group">
        <label>Empleados a pagar</label>
        <table class="tabla-empleados">
          <thead>
            <tr>
              <th>Incluir</th>
              <th>Nombre</th>
              <th>Sueldo</th>
              <th>Observaciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="config in configuraciones" :key="config.perfil">
              <td>
                <input
                  type="checkbox"
                  v-model="config.incluir_en_nomina"
                />
              </td>
              <td>{{ config.nombre }}</td>
              <td>${{ config.sueldo }}</td>
              <td>
                <input
                  type="text"
                  v-model="config.observaciones"
                  placeholder="Observaciones para el pago"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <button type="submit">Guardar configuración</button>
      <button type="button" @click="pagarNomina" style="margin-top: 10px;">Pagar Nómina</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";
import { ref, onMounted } from "vue";

export default {
  name: "PagoNomina",
  setup() {
    const configuraciones = ref([]);
    const userData = JSON.parse(localStorage.getItem("user"));

    async function cargarConfiguracion() {
      try {
        const response = await axios.get("http://localhost:8000/api/nomina/");
        configuraciones.value = response.data.map(config => ({
          ...config,
          observaciones: ""
        }));
      } catch (error) {
        console.error("Error al cargar configuración:", error);
      }
    }

    async function guardarConfiguracion() {
      try {
        const payload = configuraciones.value.map(({ perfil, incluir_en_nomina }) => ({ perfil, incluir_en_nomina }));
        await axios.post("http://localhost:8000/api/nomina/actualizar-configuracion/", {
          configuraciones: payload,
        });
        alert("Configuración guardada con éxito");
      } catch (error) {
        console.error("Error al guardar configuración:", error);
        alert("Error al guardar configuración");
      }
    }

    async function pagarNomina() {
      try {
        const confirmacion = confirm("¿Deseas continuar con el pago de nómina?");
        if (!confirmacion) return;

        for (const config of configuraciones.value) {
          if (config.incluir_en_nomina) {
            await axios.post("http://localhost:8000/api/nomina/pagar/", {
              observaciones: config.observaciones
            });
          }
        }

        alert("Nómina pagada con éxito");
        configuraciones.value.forEach(c => c.observaciones = "");
      } catch (error) {
        console.error("Error al pagar la nómina:", error);
        alert("Error al procesar el pago");
      }
    }

    onMounted(() => {
      cargarConfiguracion();
    });

    return {
      configuraciones,
      guardarConfiguracion,
      pagarNomina,
    };
  },
};
</script>

<style scoped>
.registro-producto {
  font-family: 'Poppins', sans-serif;
  max-width: auto;
  margin: 30px auto;
  padding: 25px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
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

table.tabla-empleados {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.tabla-empleados th,
.tabla-empleados td {
  padding: 10px;
  border: 1px solid #ccc;
  text-align: left;
}

.tabla-empleados th {
  background-color: #f4f4f4;
  font-weight: bold;
}

input[type="text"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: #f8f9fa;
}

input[type="checkbox"] {
  transform: scale(1.2);
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
  display: block;
  width: 100%;
  margin-top: 10px;
}

button:hover {
  background-color: #218838;
  transform: scale(1.05);
}

button:active {
  transform: scale(0.98);
}
</style>