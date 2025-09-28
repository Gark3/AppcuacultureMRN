<template>
  <div class="registro-producto">
    <h1>Registro de Proveedor</h1>
    <form @submit.prevent="registrarProveedor">
      <div class="form-group">
        <label for="nombre">Nombre</label>
        <input type="text" id="nombre" v-model="proveedor.nombre" required />
      </div>

      <div class="form-group">
        <label for="correo">Correo</label>
        <input type="email" id="correo" v-model="proveedor.correo" required />
      </div>

      <div class="form-group">
        <label for="telefono">Teléfono</label>
        <input type="text" id="telefono" v-model="proveedor.telefono" required />
      </div>

      <div class="form-group">
        <label for="descripcion">Descripción</label>
        <textarea id="descripcion" v-model="proveedor.descripcion" rows="3" required></textarea>
      </div>

      <button type="submit">Registrar Proveedor</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RegistroProveedor",
  data() {
    const userData = JSON.parse(localStorage.getItem("user"));

    return {
      proveedor: {
        fecha: this.obtenerFechaActual(), // si tu serializer la requiere
        estado: 1,
        nombre: "",
        correo: "",
        telefono: "",
        descripcion: "",
        // Ojo: tu backend dice "acuicola" y "usuario", no "acuicola_id"/"usuario_id"
        acuicola: userData ? userData.acuicola : null,
        usuario: userData ? userData.usuario_id : null,
      },
    };
  },
  methods: {
    obtenerFechaActual() {
      const hoy = new Date();
      return hoy.toISOString().split("T")[0];
    },
    async registrarProveedor() {
      try {
        console.log("Proveedor a registrar:", this.proveedor);

        // Ajusta la URL y fíjate si tu DRF ocupa '/api/proveedores/' en vez de '/api/proveedor/'
        const response = await axios.post("/proveedor/", {
          fecha: this.proveedor.fecha,
          estado: this.proveedor.estado,
          nombre: this.proveedor.nombre,
          correo: this.proveedor.correo,
          telefono: this.proveedor.telefono,      // Lo mandamos como texto
          descripcion: this.proveedor.descripcion,
          acuicola: this.proveedor.acuicola,      // No 'acuicola_id'
          usuario: this.proveedor.usuario,        // No 'usuario_id'
        });
        
        console.log("Proveedor guardado en la BD:", response.data);
        alert("Proveedor registrado con éxito!");
        
        // Reset del formulario
        this.proveedor = {
          fecha: this.obtenerFechaActual(),
          estado: 1,
          nombre: "",
          correo: "",
          telefono: "",
          descripcion: "",
          acuicola: userData ? userData.acuicola : null,
          usuario: userData ? userData.usuario_id : null,
        };
      } catch (error) {
        console.error("Error al registrar el proveedor:", error);
        if (error.response && error.response.data) {
          console.log("Detalles del error:", error.response.data);
        }
        alert("Hubo un error al registrar el proveedor. Verifica la consola.");
      }
    },
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
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}

.registro-producto:hover {
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
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
  box-shadow: 0 0 5px rgba(40, 167, 69, 0.4);
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
