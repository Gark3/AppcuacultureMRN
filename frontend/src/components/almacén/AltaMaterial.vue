<template>
  <div class="registro-producto">
    <h1>Registro de Material</h1>
    <form @submit.prevent="registrarProducto">
      <div class="form-group">
        <label for="nombre">Nombre del Material</label>
        <input type="text" id="nombre" v-model="producto.nombre" required />
      </div>

      <div class="form-group">
        <label for="rubro">Rubro</label>
        <select id="rubro" v-model="producto.rubro" required>
          <option value="">Selecciona un rubro</option>
          <option value="Alimento">Alimento</option>
          <option value="Medicamento">Medicamento</option>
          <option value="Equipo">Equipo</option>
          <option value="Reactivos">Reactivos</option>
          <option value="Mantenimiento">Mantenimiento</option>
          <option value="Limpieza">Limpieza</option>
        </select>
      </div>

      <!-- Campo de porcentaje de proteína, solo visible si rubro es "Alimento" -->
      <div class="form-group" v-if="producto.rubro === 'Alimento'">
        <label for="porcentaje_proteina">Porcentaje de Proteína</label>
        <input
          type="number"
          step="0.01"
          id="porcentaje_proteina"
          v-model.number="producto.porcentaje_proteina"
          required
        />
      </div>

      <div class="form-group">
        <label for="presentacion">Presentación</label>
        <input
          type="text"
          id="presentacion"
          v-model="producto.presentacion"
          required
        />
      </div>

      <div class="form-group">
        <label for="descripcion">Descripción</label>
        <textarea
          id="descripcion"
          v-model="producto.descripcion"
          rows="3"
          required
        ></textarea>
      </div>

      <button type="submit">Registrar Material</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";
import { ref, onMounted } from "vue";

export default {
  name: "RegistroProducto",
  setup() {
    // Obtenemos datos del usuario logueado (por ejemplo, usuario_id y acuicola)
    const userData = JSON.parse(localStorage.getItem("user"));

    // Estructura reactiva del producto
    const producto = ref({
      estado: 1, // Por ejemplo, 1 = Activo (similar a "Agregar Estanque")
      nombre: "",
      rubro: "",
      porcentaje_proteina: null,
      presentacion: "",
      descripcion: "",
      // Fecha (opcional si el backend la asigna automáticamente)
      fecha: obtenerFechaActual(),
      // Relación con usuario y acuicola
      usuario: userData ? userData.usuario_id : null,
      acuicola: userData ? userData.acuicola : null,
    });

    function obtenerFechaActual() {
      const hoy = new Date();
      return hoy.toISOString().split("T")[0]; // Formato YYYY-MM-DD
    }

    // Lógica para registrar el material
    async function registrarProducto() {
      try {
        // Si el rubro no es "Alimento", forzamos el porcentaje de proteína a 0
        if (producto.value.rubro !== "Alimento") {
          producto.value.porcentaje_proteina = 0;
        }

        console.log("Producto a registrar:", producto.value);

        // Llamada al backend (similar a "Agregar Estanque")
        // Ajusta la URL según tu endpoint real
        const response = await axios.post(
          "http://localhost:8000/api/producto/",
          {
            estado: producto.value.estado,
            nombre: producto.value.nombre,
            rubro: producto.value.rubro,
            porcentaje_proteina: producto.value.porcentaje_proteina,
            presentacion: producto.value.presentacion,
            descripcion: producto.value.descripcion,
            // Si tu backend lo requiere, podrías enviar la fecha
            // fecha: producto.value.fecha,

            // Relación con usuario y acuicola (similar a "Agregar Estanque")
            usuario: producto.value.usuario,
            acuicola: producto.value.acuicola,
          }
        );

        console.log("Producto guardado en la BD:", response.data);
        alert("Material registrado con éxito!");

        // Resetear el formulario
        producto.value = {
          estado: 1,
          nombre: "",
          rubro: "",
          porcentaje_proteina: null,
          presentacion: "",
          descripcion: "",
          fecha: obtenerFechaActual(),
          usuario: userData ? userData.usuario_id : null,
          acuicola: userData ? userData.acuicola : null,
        };
      } catch (error) {
        console.error("Error al registrar el material:", error);
        alert(
          "Hubo un error al registrar el material. Revisa la consola para más detalles."
        );
      }
    }

    onMounted(() => {
      // Aquí podrías cargar datos iniciales si lo requieres
    });

    return {
      producto,
      registrarProducto,
      obtenerFechaActual,
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

.registro-producto:hover {
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

input,
select,
textarea {
  width: 100%;
  padding: 12px;
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease-in-out;
  background: #f8f9fa;
}

input:focus,
select:focus,
textarea:focus {
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
  display: block;
  width: 100%;
}

button:hover {
  background-color: #218838;
  transform: scale(1.05);
}

button:active {
  transform: scale(0.98);
}
</style>
