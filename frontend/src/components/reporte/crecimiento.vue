<template>
  <div class="grafico-container">
    <h1>Visualización de Crecimiento por Estanque</h1>

    <form class="form-seleccion" @submit.prevent="actualizarGrafico">
      <div class="form-group">
        <label for="estanque">Seleccione un Estanque:</label>
        <select v-model="estanqueSeleccionado" required>
          <option v-for="e in estanques" :key="e.id_estanque" :value="e.id_estanque">{{ e.nombre }}</option>
        </select>
      </div>

      <div class="form-group">
        <label for="ciclo">Seleccione un Ciclo:</label>
        <select v-model="siembraSeleccionada" required>
          <option v-for="c in ciclos" :key="c.id_siembra" :value="c.id_siembra">{{ formatDate(c.fecha) }} - {{ c.especie }}</option>
        </select>
      </div>

      <div class="form-group">
        <label for="periodo">Seleccione el Periodo de Tiempo:</label>
        <select v-model="periodoSeleccionado" required>
          <option v-for="p in periodos" :key="p" :value="p">{{ p }}</option>
        </select>
      </div>

      <div class="form-group">
        <label for="parametro">Seleccione el Rubro:</label>
        <select v-model="parametroSeleccionado" required>
          <option value="Todos los rubros">Todos los rubros</option>
          <option v-for="r in parametrosActuales" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>

      <button type="submit">Generar Gráfico(s)</button>
    </form>

    <!-- GRÁFICO GLOBAL -->
    <div class="grafico-individual">
      <h3>{{ parametroSeleccionado }}</h3>
      <canvas id="grafico"></canvas>
    </div>

    <!-- TABLAS DE DISTRIBUCIÓN -->
    <div v-for="(segmentos, fecha) in distribucionTallas" :key="fecha" class="grafico-individual">
      <h3>Distribución de Tallas - {{ fecha }}</h3>
      <table>
        <thead>
          <tr>
            <th>Rango (gr)</th>
            <th>Cantidad</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="segmento in segmentos" :key="segmento.etiqueta">
            <td>{{ segmento.etiqueta }}</td>
            <td>{{ segmento.cantidad }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <button type="button" class="btn-generar" @click="exportarReporte">Exportar Reporte</button>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed, nextTick } from "vue";
import axios from "@/services/axios";
import Chart from "chart.js/auto";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

export default {
  name: "Crecimiento",
  setup() {
    const estanques = ref([]);
    const ciclos = ref([]);
    const datos = ref([]);
    const rubros = ref([]);
    const parametrosActuales = ref([]);
    const distribucionTallas = ref({});
    const chartInstances = ref({});

    const parametroSeleccionado = ref("Todos los rubros");
    const periodoSeleccionado = ref("7 días");
    const estanqueSeleccionado = ref(null);
    const siembraSeleccionada = ref(null);

    const diasPorPeriodo = {
      "Hoy": 1, "7 días": 7, "15 días": 15, "1 mes": 30,
      "2 meses": 60, "3 meses": 90, "4 meses": 120,"5 meses": 150,
      "6 meses": 180,"7 meses": 210,
    };

    const periodos = Object.keys(diasPorPeriodo);
    const mostrarTodosParametros = computed(() => parametroSeleccionado.value === "Todos los rubros");

    const formatDate = (fecha) => new Date(fecha).toISOString().split("T")[0];

    const obtenerEstanques = async () => {
      const user = JSON.parse(localStorage.getItem("user"));
      const res = await axios.get("/estanque/");
      estanques.value = res.data.filter(e => e.estatus && e.acuicola === user.acuicola);
    };

    const obtenerCiclos = async () => {
      const res = await axios.get("/siembra/");
      ciclos.value = res.data.filter(s => s.estanque === estanqueSeleccionado.value);
    };

    const obtenerRubros = async () => {
      const [crecimientos, rubrosData] = await Promise.all([
        axios.get("/crecimiento/"),
        axios.get("/rubro/")
      ]);
      rubros.value = rubrosData.data;
      const usados = crecimientos.data.filter(c => c.siembra === siembraSeleccionada.value);
      const únicos = [...new Set(usados.map(c => c.rubro))];
      parametrosActuales.value = únicos.map(id => {
        const rub = rubros.value.find(r => r.id_rubro === id);
        return rub ? `${rub.nombre} (${rub.unidad})` : null;
      }).filter(Boolean);
    };

    const obtenerDatos = async () => {
      const res = await axios.get("/crecimiento/");
      datos.value = res.data.filter(d => d.siembra === siembraSeleccionada.value);
    };

    const actualizarGrafico = async () => {
      await obtenerDatos();
      await nextTick();

      const dias = diasPorPeriodo[periodoSeleccionado.value];
      const hoy = new Date();
      const inicio = new Date();
      inicio.setDate(hoy.getDate() - (dias - 1));

      const rubrosSeleccionados = mostrarTodosParametros.value
        ? parametrosActuales.value
        : [parametroSeleccionado.value];

      // Agrupación
      const globalData = {};
      rubrosSeleccionados.forEach(param => {
        const rubroObj = rubros.value.find(r => param.includes(r.nombre));
        if (!rubroObj) return;
        const registros = datos.value.filter(d =>
          d.rubro === rubroObj.id_rubro && new Date(d.fecha) >= inicio
        );
        registros.forEach(r => {
          const fecha = formatDate(r.fecha);
          if (!globalData[param]) globalData[param] = {};
          if (!globalData[param][fecha]) globalData[param][fecha] = [];
          globalData[param][fecha].push(r.medicion);
        });
      });

      // Limpiar gráfico
      if (chartInstances.value.individual) {
        chartInstances.value.individual.destroy();
      }

      const ctx = document.getElementById("grafico").getContext("2d");
      chartInstances.value.individual = new Chart(ctx, {
        type: "line",
        data: {
          labels: Object.keys(globalData[rubrosSeleccionados[0]] || {}),
          datasets: rubrosSeleccionados.map((param, i) => ({
            label: param,
            data: Object.entries(globalData[param] || {}).map(([_, vals]) =>
              vals.reduce((a, b) => a + b, 0) / vals.length),
            borderColor: "#28a745",
            backgroundColor: "rgba(40, 167, 69, 0.2)",
            borderWidth: 2
          }))
        },
        options: {
          responsive: true,
          plugins: { legend: { display: true } },
          scales: {
            x: {
              title: { display: true, text: "Fecha" },
              ticks: { maxRotation: 90, minRotation: 90 },
            },
            y: {
              title: { display: true, text: "Medición promedio" },
              beginAtZero: true
            }
          }
        }
      });

      // Distribución (solo tablas)
      distribucionTallas.value = {};
      const agruparPorFecha = {};
      datos.value
        .filter(d => new Date(d.fecha) >= inicio)
        .forEach(d => {
          const fecha = formatDate(d.fecha);
          if (!agruparPorFecha[fecha]) agruparPorFecha[fecha] = [];
          agruparPorFecha[fecha].push(d.medicion);
        });

      for (const [fecha, mediciones] of Object.entries(agruparPorFecha)) {
        const min = Math.min(...mediciones);
        const max = Math.max(...mediciones);
        const rango = (max - min) / 5 || 1;
        const segmentos = Array(5).fill(0).map((_, i) => ({
          etiqueta: `${(min + i * rango).toFixed(1)} - ${(min + (i + 1) * rango).toFixed(1)}`,
          cantidad: 0
        }));
        mediciones.forEach(val => {
          const idx = Math.min(Math.floor((val - min) / rango), 4);
          segmentos[idx].cantidad += 1;
        });
        distribucionTallas.value[fecha] = segmentos;
      }
    };

    const exportarReporte = async () => {
      const doc = new jsPDF();
      doc.text("Reporte de Crecimiento", 10, 10);
      doc.text(`Estanque: ${estanqueSeleccionado.value}`, 10, 20);
      doc.text(`Ciclo: ${siembraSeleccionada.value}`, 10, 30);
      doc.text(`Periodo: ${periodoSeleccionado.value}`, 10, 40);
      doc.text(`Rubro: ${parametroSeleccionado.value}`, 10, 50);

      const canvas = document.getElementById("grafico");
      if (canvas) {
        const imgData = canvas.toDataURL("image/png");
        doc.addImage(imgData, "PNG", 10, 60, 190, 90);
      }

      let y = 160;
      for (const [fecha, segmentos] of Object.entries(distribucionTallas.value)) {
        if (y > 230) {
          doc.addPage();
          y = 20;
        }
        doc.text(`Distribución - ${fecha}`, 10, y);
        autoTable(doc, {
          startY: y + 5,
          head: [["Rango (gr)", "Cantidad"]],
          body: segmentos.map(s => [s.etiqueta, s.cantidad]),
        });
        y = doc.lastAutoTable.finalY + 10;
      }

      doc.save(`reporte_crecimiento_${Date.now()}.pdf`);
    };

    watch(estanqueSeleccionado, obtenerCiclos);
    watch(siembraSeleccionada, obtenerRubros);
    onMounted(obtenerEstanques);

    return {
      estanques,
      ciclos,
      parametroSeleccionado,
      parametrosActuales,
      periodoSeleccionado,
      periodos,
      estanqueSeleccionado,
      siembraSeleccionada,
      formatDate,
      actualizarGrafico,
      exportarReporte,
      distribucionTallas
    };
  }
};
</script>

<style scoped>
/* Tu estilo ya incluido, no modificado */
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
  max-width: 100%;
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
