<template>
  <div class="registro-producto">
    <h1>Gestión de Salarios</h1>

    <div class="tabla-responsive">
      <table class="tabla-empleados">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Correo</th>
            <th>Salario actual</th>
            <th>Nuevo salario</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="perfil in perfiles" :key="perfil.id">
            <td>{{ perfil.user.username }}</td>
            <td>{{ perfil.user.email }}</td>
            <td>${{ perfil.sueldo.toFixed(2) }}</td>
            <td>
              <input
                type="number"
                v-model.number="perfil.sueldoEditable"
                step="0.01"
                min="0"
              />
            </td>
            <td class="acciones">
              <button @click="actualizarSalario(perfil)">Guardar</button>
              <button @click="verHistorial(perfil)">Historial</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal flotante para historial -->
    <div v-if="historialActivo" class="historial-modal">
      <div>
        <h2>Historial de Sueldo: {{ historialNombre }}</h2>
        <div class="tarjetas-historial">
          <div
            v-for="registro in historialPaginado"
            :key="registro.id"
            class="tarjeta-historial"
          >
            <p><strong>Fecha:</strong> {{ new Date(registro.fecha_cambio).toLocaleDateString() }}</p>
            <p><strong>Anterior:</strong> ${{ registro.sueldo_anterior.toFixed(2) }}</p>
            <p><strong>Nuevo:</strong> ${{ registro.sueldo_nuevo.toFixed(2) }}</p>
            <p><strong>Cambiado por:</strong> {{ registro.cambiado_por_username }}</p>
          </div>
        </div>
        <div class="paginacion">
          <button @click="historialPagina--" :disabled="historialPagina === 1">Anterior</button>
          <span>Página {{ historialPagina }} de {{ totalPaginasHistorial }}</span>
          <button @click="historialPagina++" :disabled="historialPagina === totalPaginasHistorial">Siguiente</button>
        </div>
        <button @click="cerrarHistorial">Cerrar</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/services/axios";

export default {
  name: "Salarios",
  data() {
    return {
      perfiles: [],
      historialSueldo: [],
      historialActivo: false,
      historialNombre: "",
      historialPagina: 1,
      historialPorPagina: 5
    };
  },
  computed: {
    historialPaginado() {
      const inicio = (this.historialPagina - 1) * this.historialPorPagina;
      return this.historialSueldo.slice(inicio, inicio + this.historialPorPagina);
    },
    totalPaginasHistorial() {
      return Math.ceil(this.historialSueldo.length / this.historialPorPagina);
    }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user || !user.access) {
      alert("Sesión no válida. Inicia sesión de nuevo.");
      this.$router.push("/login");
    }
    this.cargarPerfiles();
  },
  methods: {
    async cargarPerfiles() {
      try {
        const res = await axios.get("perfiles/");
        this.perfiles = res.data.map((p) => ({
          ...p,
          sueldoEditable: p.sueldo || 0,
        }));
      } catch (error) {
        console.error("Error al cargar perfiles:", error);
        alert("No se pudieron cargar los perfiles.");
      }
    },
    async actualizarSalario(perfil) {
      try {
        const diferencia = perfil.sueldoEditable - (perfil.sueldo || 0);
        if (diferencia === 0) {
          alert("No se han hecho cambios en el salario.");
          return;
        }

        await axios.patch(`perfiles/${perfil.id}/`, {
          sueldo: perfil.sueldoEditable,
        });

        await axios.post("historial-sueldo/", {
          perfil: perfil.id,
          sueldo_anterior: perfil.sueldo,
          sueldo_nuevo: perfil.sueldoEditable,
          cambiado_por: JSON.parse(localStorage.getItem("user"))?.usuario_id,
        });

        perfil.sueldo = perfil.sueldoEditable;
        alert(`Sueldo de ${perfil.user.username} actualizado.`);
      } catch (error) {
        console.error("Error al actualizar sueldo:", error);
        alert("No se pudo actualizar el sueldo.");
      }
    },
    async verHistorial(perfil) {
      try {
        const res = await axios.get(`historial-sueldo/?perfil=${perfil.id}`);
        this.historialSueldo = res.data.map(r => ({
          ...r,
          cambiado_por_username: r.cambiado_por_username || "---"
        }));
        this.historialNombre = perfil.user.username;
        this.historialPagina = 1;
        this.historialActivo = true;
      } catch (error) {
        console.error("Error al cargar historial:", error);
        alert("No se pudo cargar el historial de sueldos.");
      }
    },
    cerrarHistorial() {
      this.historialSueldo = [];
      this.historialNombre = "";
      this.historialActivo = false;
    }
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

.tabla-responsive {
  width: 100%;
  overflow-x: auto;
}

table.tabla-empleados {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  margin-bottom: 20px;
  min-width: 600px;
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

input[type="number"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: #f8f9fa;
}

button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 10px 14px;
  font-size: 14px;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease-in-out;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-right: 5px;
}

button:hover {
  background-color: #218838;
  transform: scale(1.05);
}

button:active {
  transform: scale(0.98);
}

.historial-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.4);
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px 20px;
}

.historial-modal > div {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  max-width: auto;
  width: 100%;
}

.tarjetas-historial {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 10px;
}

.tarjeta-historial {
  background: white;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.08);
  font-size: 14px;
}

.tarjeta-historial p {
  margin: 4px 0;
  color: #333;
}

.paginacion {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
}
.paginacion button {
  padding: 6px 10px;
  border: none;
  background: #28a745;
  color: white;
  border-radius: 6px;
  cursor: pointer;
}
.paginacion button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  h1 {
    font-size: 20px;
  }

  table.tabla-empleados {
    font-size: 12px;
  }

  button {
    font-size: 12px;
    padding: 8px 10px;
  }
}
</style>