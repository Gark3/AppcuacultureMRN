<template>
  <div class="reporte-estanque">
    <h1>Reporte de Estanque</h1>

    <form @submit.prevent="obtenerCiclos">
      <div class="form-group">
        <label for="estanque">Selecciona el estanque:</label>
        <select v-model="filtro.estanque" id="estanque" required>
          <!-- Opción para mostrar ciclos activos de todos los estanques -->
          <option value="todos-activos">Ciclos Actuales (Todos los Estanques)</option>
          <!-- Opciones individuales -->
          <option v-for="estanque in estanques" :key="estanque.id_estanque" :value="estanque.id_estanque">
            {{ estanque.nombre }}
          </option>
        </select>
      </div>

      <button type="submit" class="btn-generar" :disabled="loading">
        {{ loading ? 'Cargando...' : 'Obtener Ciclos' }}
      </button>
    </form>

    <!-- Si se obtuvieron ciclos -->
    <div v-if="ciclos.length">
      <!-- Modo "todos-activos": mostrar solo ciclos activos y opción de reporte consolidado -->
      <div v-if="filtro.estanque === 'todos-activos'">
        <h2>CICLOS ACTUALES</h2>
        <button @click="exportarPDFTodos" class="btn-generar">
          Obtener Reporte de Todos los Ciclos Actuales
        </button>
        <table>
          <thead>
            <tr>
              <th>Ciclo</th>
              <th>Fecha de Siembra</th>
              <th>Fecha de Cosecha</th>
              <th>Vista previa</th>
              <th>Reporte</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(ciclo, index) in activeCiclos" :key="ciclo.id_siembra">
              <td>{{ index + 1 }}</td>
              <td>{{ ciclo.fecha }}</td>
              <td>{{ ciclo.fecha_cosecha || 'En proceso' }}</td>
              <td>
                <button @click="vistaPrevia(ciclo)">Vista previa</button>
              </td>
              <td>
                <button @click="exportarPDF(ciclo)">Exportar PDF</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Modo por estanque individual: se muestran ciclos activos y finalizados -->
      <div v-else>
        <div v-if="activeCiclos.length">
          <h2>CICLOS ACTUALES</h2>
          <table>
            <thead>
              <tr>
                <th>Ciclo</th>
                <th>Fecha de Siembra</th>
                <th>Fecha de Cosecha</th>
                <th>Vista previa</th>
                <th>Reporte</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ciclo, index) in activeCiclos" :key="ciclo.id_siembra">
                <td>{{ index + 1 }}</td>
                <td>{{ ciclo.fecha }}</td>
                <td>{{ ciclo.fecha_cosecha || 'En proceso' }}</td>
                <td>
                  <button @click="vistaPrevia(ciclo)">Vista previa</button>
                </td>
                <td>
                  <button @click="exportarPDF(ciclo)">Exportar PDF</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="historicalCiclos.length">
          <h2>CICLOS FINALIZADOS</h2>
          <table>
            <thead>
              <tr>
                <th>Ciclo</th>
                <th>Fecha de Siembra</th>
                <th>Fecha de Cosecha</th>
                <th>Vista previa</th>
                <th>Reporte</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ciclo, index) in historicalCiclos" :key="ciclo.id_siembra">
                <td>{{ index + 1 }}</td>
                <td>{{ ciclo.fecha }}</td>
                <td>{{ ciclo.fecha_cosecha }}</td>
                <td>
                  <button @click="vistaPrevia(ciclo)">Vista previa</button>
                </td>
                <td>
                  <button @click="exportarPDF(ciclo)">Exportar PDF</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Vista previa individual del ciclo -->
    <div v-if="vista">
      <h2>Vista previa del ciclo</h2>
      <p><strong>Fecha de Siembra:</strong> {{ vista.fecha }}</p>
      <p><strong>Fecha de Cosecha:</strong> {{ vista.fecha_cosecha || 'En proceso' }}</p>
      <p><strong>Especie:</strong> {{ vista.especie }}</p>
      <p><strong>Organismos:</strong> {{ vista.cantidad_organismos }}</p>
      <p><strong>Biomasa Estimada:</strong> {{ vista.biomasa || 'N/A' }}</p>
      <p><strong>FCA:</strong> {{ vista.fca || 'N/A' }}</p>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, watch } from "vue";
import axios from '@/services/axios';
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

export default {
  setup() {
    const estanques = ref([]);
    const ciclos = ref([]);
    const filtro = reactive({ estanque: '' });
    const loading = ref(false);
    const vista = ref(null);

    const obtenerEstanques = async () => {
      try {
        const user = JSON.parse(localStorage.getItem("user"));
        const response = await axios.get("/estanque/");
        estanques.value = response.data.filter(e => e.acuicola === user.acuicola);
      } catch (error) {
        console.error("Error al obtener estanques:", error);
      }
    };

    const obtenerCiclos = async () => {
      loading.value = true;
      ciclos.value = [];
      try {
        const response = await axios.get(`/siembra/`);
        let siembras = response.data;
        // Filtrar si se selecciona un estanque en particular
        if (filtro.estanque !== "todos-activos") {
          siembras = siembras.filter(s => s.estanque === filtro.estanque);
        }
        const cosechas = await axios.get('/cosecha/');
        const dataCosechas = cosechas.data;
        ciclos.value = siembras.map(siembra => {
          const cosecha = dataCosechas.find(c => c.siembra === siembra.id_siembra);
          return {
            ...siembra,
            fecha_cosecha: cosecha ? cosecha.fecha : null
          };
        });
      } catch (error) {
        console.error("Error al obtener ciclos:", error);
        alert("Error al obtener ciclos");
      } finally {
        loading.value = false;
      }
    };

    // Computed para separar ciclos activos (sin fecha de cosecha) y finalizados
    const activeCiclos = computed(() =>
      ciclos.value.filter(ciclo => !ciclo.fecha_cosecha)
    );
    const historicalCiclos = computed(() =>
      ciclos.value.filter(ciclo => ciclo.fecha_cosecha)
    );

    // Watcher para limpiar los ciclos al cambiar la opción del filtro
    watch(() => filtro.estanque, () => {
      ciclos.value = [];
    });

    // Genera un PDF individual para un ciclo
    const exportarPDF = (ciclo) => {
      const doc = new jsPDF();
      const nombreArchivo = `Reporte_Estanque_${filtro.estanque}_Siembra_${ciclo.fecha}_${ciclo.fecha_cosecha || 'EnProceso'}.pdf`;
      doc.text(`Reporte de Ciclo del Estanque`, 10, 10);
      autoTable(doc, {
        head: [["Campo", "Valor"]],
        body: [
          ["Fecha de Siembra", ciclo.fecha],
          ["Fecha de Cosecha", ciclo.fecha_cosecha || "En proceso"],
          ["Especie", ciclo.especie],
          ["Número de Organismos", ciclo.cantidad_organismos],
          ["Biomasa Estimada", ciclo.biomasa || "N/A"],
          ["FCA", ciclo.fca || "N/A"]
        ]
      });
      doc.save(nombreArchivo);
    };

    // Genera un PDF combinando todos los ciclos activos (de todos los estanques)
    // omitiendo la fecha de siembra para evitar incongruencias
    const exportarPDFTodos = () => {
      const doc = new jsPDF();
      doc.text(`Reporte de Ciclos Actuales (Todos los Estanques)`, 10, 10);
      let startY = 20;
      activeCiclos.value.forEach((ciclo, index) => {
        doc.text(`Ciclo ${index + 1}`, 10, startY);
        startY += 10;
        autoTable(doc, {
          startY: startY,
          head: [["Campo", "Valor"]],
          body: [
            ["Fecha de Cosecha", ciclo.fecha_cosecha ? ciclo.fecha_cosecha : "En proceso"],
            ["Especie", ciclo.especie],
            ["Número de Organismos", ciclo.cantidad_organismos],
            ["Biomasa Estimada", ciclo.biomasa || "N/A"],
            ["FCA", ciclo.fca || "N/A"]
          ],
          theme: 'grid',
          margin: { left: 10, right: 10 }
        });
        startY = doc.lastAutoTable.finalY + 10;
      });
      doc.save(`Reporte_Ciclos_Activos_Todos_Estanques.pdf`);
    };

    const vistaPrevia = (ciclo) => {
      vista.value = ciclo;
    };

    onMounted(obtenerEstanques);

    return {
      estanques,
      ciclos,
      filtro,
      obtenerCiclos,
      exportarPDF,
      exportarPDFTodos,
      vistaPrevia,
      vista,
      loading,
      activeCiclos,
      historicalCiclos
    };
  }
};
</script>

<style scoped>
.reporte-estanque {
  font-family: 'Poppins', sans-serif;
  max-width: auto;
  margin: 0 auto;
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

h1, h2 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
}

select {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  font-size: 14px;
}

th, td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: center;
}

button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #0056b3;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-generar {
  margin: 10px 0;
}
</style>