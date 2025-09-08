<template>
  <div class="grafico-container">
    <h1>Visualización de Parámetros por Estanque</h1>
    <form class="form-seleccion" @submit.prevent="actualizarGrafico">
      <!-- Selección de Estanque -->
      <div class="form-group">
        <label for="estanque">Seleccione un Estanque:</label>
        <select id="estanque" v-model="estanqueSeleccionado" required>
          <option v-for="estanque in estanques" :key="estanque.id_estanque" :value="estanque.id_estanque">
            {{ estanque.nombre }}
          </option>
        </select>
      </div>
      <!-- Selección de Ciclo -->
      <div class="form-group">
        <label for="ciclo">Seleccione un Ciclo:</label>
        <select id="ciclo" v-model="siembraSeleccionada" required>
          <option v-for="ciclo in ciclos" :key="ciclo.id_siembra" :value="ciclo.id_siembra">
            {{ formatDate(ciclo.fecha) }} - {{ ciclo.especie }}
          </option>
        </select>
      </div>
      <!-- Selección de Periodo -->
      <div class="form-group">
        <label for="periodo">Seleccione el Periodo de Tiempo:</label>
        <select id="periodo" v-model="periodoSeleccionado" required>
          <option v-for="periodo in periodos" :key="periodo" :value="periodo">
            {{ periodo }}
          </option>
        </select>
      </div>
      <!-- Selección de Parámetro -->
      <div class="form-group">
        <label for="parametro">Seleccione el Parámetro:</label>
        <select id="parametro" v-model="parametroSeleccionado" required>
          <option value="Todos los parámetros">Todos los parámetros</option>
          <option v-for="param in parametrosActuales" :key="param" :value="param">
            {{ param }}
          </option>
        </select>
      </div>
      <button type="submit">Generar Gráfico(s)</button>
    </form>

    <!-- Sección de gráficos y tablas -->
    <div v-if="mostrarTodosParametros">
      <!-- Si se selecciona "Todos los parámetros": generar múltiples secciones -->
      <div v-for="param in parametrosActuales" :key="param" class="grafico-individual">
        <h3>{{ param }}</h3>
        <canvas :id="`grafico-${param.replaceAll(' ', '-')}`" style="max-width: 100%; margin-top: 20px;"></canvas>
        <!-- Tabla de datos para el parámetro -->
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>{{ param }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in tableDataTodos[param]" :key="index">
              <td>{{ item.fecha }}</td>
              <td>{{ item.valor }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else>
      <!-- Caso de parámetro individual -->
      <canvas id="grafico" style="max-width: 100%; margin-top: 20px;"></canvas>
      <!-- Tabla de datos para el parámetro seleccionado -->
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>{{ parametroSeleccionado }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in tableData" :key="index">
            <td>{{ item.fecha }}</td>
            <td>{{ item.valor }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <button type="button" @click="exportarReporte" class="btn-generar" style="margin-top: 20px;">
      Exportar Reporte
    </button>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from "vue";
import axios from "@/services/axios";
import Chart from "chart.js/auto";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

export default {
  name: "GraficoEstanque",
  setup() {
    // Reactivos para selección y datos
    const estanques = ref([]);
    const ciclos = ref([]);
    const datos = ref([]);

    const estanqueSeleccionado = ref(null);
    const siembraSeleccionada = ref(null);
    const parametroSeleccionado = ref("Oxígeno disuelto");
    const periodoSeleccionado = ref("7 días");

    // Para almacenar instancias de gráficos
    const chartInstances = ref({});

    // Para almacenar datos de la tabla
    const tableData = ref([]); // Caso individual
    const tableDataTodos = ref({}); // Caso "Todos los parámetros" (objeto: clave = parámetro)

    const periodos = ["Hoy", "7 días", "15 días", "1 mes", "2 meses", "3 meses", "4 meses","12 meses"];
    const parametrosActuales = [
      "Temperatura",
      "Oxígeno disuelto",
      "pH",
      "Nitritos",
      "Nitratos",
      "Sulfato",
      "Fosfato",
      "Cloro",
      "Salinidad",
    ];

    const mostrarTodosParametros = computed(() => parametroSeleccionado.value === "Todos los parámetros");

    const normalizarCampo = (nombre) => {
      const mapa = {
        "Temperatura": "temperatura",
        "Oxígeno disuelto": "oxigeno_disuelto",
        "pH": "ph",
        "Nitritos": "nitritos",
        "Nitratos": "nitratos",
        "Sulfato": "sulfato",
        "Fosfato": "fosfato",
        "Cloro": "cloro",
        "Salinidad": "salinidad",
      };
      return mapa[nombre] || nombre.toLowerCase().replaceAll(" ", "_");
    };

    // Función para formatear fechas (AAAA-MM-DD)
    const formatDate = (dateStr) => {
      const date = new Date(dateStr);
      return date.toISOString().split('T')[0];
    };

    // Obtención de estanques
    const obtenerEstanques = async () => {
      const user = JSON.parse(localStorage.getItem("user"));
      const res = await axios.get("/estanque/");
      estanques.value = res.data.filter(e => e.estatus && e.acuicola === user.acuicola);
    };

    // Obtención de ciclos para el estanque seleccionado
    const obtenerCiclos = async () => {
      const res = await axios.get("/siembra/");
      ciclos.value = res.data.filter(s => s.estanque === estanqueSeleccionado.value);
    };

    // Obtención de datos de calidad del agua para el ciclo seleccionado
    const obtenerDatosCalidadAgua = async () => {
      const res = await axios.get("/calidad-agua/");
      datos.value = res.data.filter(d => d.siembra === siembraSeleccionada.value);
    };

    const diasPorPeriodo = {
      "Hoy": 1,
      "7 días": 7,
      "15 días": 15,
      "1 mes": 30,
      "2 meses": 60,
      "3 meses": 90,
      "4 meses": 120,
      "12 meses": 365,
    };

    // Función para generar gráficos y preparar datos de tabla
    const actualizarGrafico = async () => {
      await obtenerDatosCalidadAgua();
      const dias = diasPorPeriodo[periodoSeleccionado.value];
      const hoy = new Date();
      let inicio = new Date();
      inicio.setDate(hoy.getDate() - (dias - 1));

      // Si se selecciona "Todos los parámetros", se generan gráficos para cada parámetro
      if (mostrarTodosParametros.value) {
        parametrosActuales.forEach(param => {
          const field = normalizarCampo(param);
          const filtrados = datos.value.filter(d => {
            const fecha = new Date(d.fecha);
            return fecha >= inicio && fecha <= hoy && d[field] !== undefined;
          });
          filtrados.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
          const etiquetas = filtrados.map(d => formatDate(d.fecha));
          const valores = filtrados.map(d => d[field]);
          // Guardar datos para la tabla
          tableDataTodos.value[param] = filtrados.map(d => ({
            fecha: formatDate(d.fecha),
            valor: d[field]
          }));

          const canvasId = `grafico-${param.replaceAll(' ', '-')}`;
          const canvasElem = document.getElementById(canvasId);
          if (!canvasElem) return;
          const ctx = canvasElem.getContext("2d");
          if (chartInstances.value[param]) {
            chartInstances.value[param].destroy();
          }
          chartInstances.value[param] = new Chart(ctx, {
            type: "line",
            data: {
              labels: etiquetas,
              datasets: [
                {
                  label: param,
                  data: valores,
                  borderColor: "#28a745",
                  backgroundColor: "rgba(40, 167, 69, 0.2)",
                  borderWidth: 2,
                },
              ],
            },
            options: {
              responsive: true,
              plugins: { legend: { display: true } },
              scales: {
                x: {
                  title: { display: true, text: "Fecha" },
                  ticks: { maxRotation: 90, minRotation: 90 },
                },
                y: { title: { display: true, text: "Valor" }, beginAtZero: true },
              },
            },
          });
        });
      } else {
        // Caso de parámetro individual
        const field = normalizarCampo(parametroSeleccionado.value);
        const filtrados = datos.value.filter(d => {
          const fecha = new Date(d.fecha);
          return fecha >= inicio && fecha <= hoy && d[field] !== undefined;
        });
        filtrados.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
        const etiquetas = filtrados.map(d => formatDate(d.fecha));
        const valores = filtrados.map(d => d[field]);
        tableData.value = filtrados.map(d => ({
          fecha: formatDate(d.fecha),
          valor: d[field]
        }));
        const canvasElem = document.getElementById("grafico");
        const ctx = canvasElem.getContext("2d");
        if (chartInstances.value["individual"]) {
          chartInstances.value["individual"].destroy();
        }
        chartInstances.value["individual"] = new Chart(ctx, {
          type: "line",
          data: {
            labels: etiquetas,
            datasets: [
              {
                label: parametroSeleccionado.value,
                data: valores,
                borderColor: "#28a745",
                backgroundColor: "rgba(40, 167, 69, 0.2)",
                borderWidth: 2,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: { legend: { display: true } },
            scales: {
              x: {
                title: { display: true, text: "Fecha" },
                ticks: { maxRotation: 90, minRotation: 90 },
              },
              y: { title: { display: true, text: "Valor" }, beginAtZero: true },
            },
          },
        });
      }
    };

    // Función para exportar el reporte en PDF, incluyendo las gráficas y tablas
    const exportarReporte = () => {
      const doc = new jsPDF();
      doc.text(`Reporte de Parámetros Fisicoquímicos`, 10, 10);
      doc.text(`Estanque: ${estanqueSeleccionado.value}`, 10, 20);
      doc.text(`Ciclo: ${siembraSeleccionada.value}`, 10, 30);
      doc.text(`Periodo: ${periodoSeleccionado.value}`, 10, 40);
      doc.text(`Parámetro: ${parametroSeleccionado.value}`, 10, 50);
      
      if (mostrarTodosParametros.value) {
        // Recorrer cada parámetro y agregar la gráfica y datos en páginas separadas
        parametrosActuales.forEach((param, index) => {
          const canvasId = `grafico-${param.replaceAll(' ', '-')}`;
          const canvas = document.getElementById(canvasId);
          if (canvas) {
            const imgData = canvas.toDataURL("image/png");
            doc.addPage();
            doc.text(`Parámetro: ${param}`, 10, 10);
            doc.addImage(imgData, "PNG", 10, 20, 190, 100);
            // Agregar la tabla de datos correspondiente
            const dataRows = tableDataTodos.value[param].map(item => [item.fecha, item.valor]);
            autoTable(doc, {
              startY: 130,
              head: [["Fecha", param]],
              body: dataRows,
              theme: 'grid',
            });
          }
        });
        doc.save(`Reporte_Parametros_Todos_${estanqueSeleccionado.value}_${siembraSeleccionada.value}.pdf`);
      } else {
        // Caso individual
        const canvas = document.getElementById("grafico");
        if (!canvas) {
          alert("No se encontró la gráfica para exportar.");
          return;
        }
        const imgData = canvas.toDataURL("image/png");
        doc.addImage(imgData, "PNG", 10, 60, 190, 100);
        // Agregar la tabla de datos
        const dataRows = tableData.value.map(item => [item.fecha, item.valor]);
        autoTable(doc, {
          startY: 170,
          head: [["Fecha", parametroSeleccionado.value]],
          body: dataRows,
          theme: 'grid',
        });
        doc.save(`Reporte_Parametros_${estanqueSeleccionado.value}_${siembraSeleccionada.value}.pdf`);
      }
    };

    // Actualizar lista de ciclos cuando cambia el estanque seleccionado
    watch(estanqueSeleccionado, () => {
      obtenerCiclos();
    });

    onMounted(() => {
      obtenerEstanques();
    });

    return {
      estanques,
      ciclos,
      datos,
      estanqueSeleccionado,
      siembraSeleccionada,
      parametroSeleccionado,
      periodoSeleccionado,
      periodos,
      parametrosActuales,
      actualizarGrafico,
      exportarReporte,
      formatDate,
      mostrarTodosParametros,
      tableData,
      tableDataTodos,
    };
  },
};
</script>

<style scoped>
.grafico-container {
  font-family: 'Poppins', sans-serif;
  max-width: auto;
  margin: 30px auto;
  padding: 25px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}

.form-seleccion {
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

select {
  width: 100%;
  padding: 12px;
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease-in-out;
  background: #f8f9fa;
}

select:focus {
  border-color: #28a745;
  outline: none;
  box-shadow: 0px 0px 5px rgba(40, 167, 69, 0.4);
}

canvas {
  margin-top: 20px;
}

.grafico-individual {
  margin-bottom: 30px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 14px;
}

th, td {
  padding: 8px;
  border: 1px solid #ddd;
  text-align: center;
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

.btn-generar {
  margin-top: 20px;
}
</style>
