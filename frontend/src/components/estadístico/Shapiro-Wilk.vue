<template>
  <div class="grafico-container">
    <h1>Prueba de Normalidad Shapiro-Wilk</h1>

    <form class="form-seleccion" @submit.prevent="ejecutarPrueba">
      <div class="form-group">
        <label for="estanque">Estanque:</label>
        <select v-model="estanqueSeleccionado" id="estanque" required>
          <option disabled value="">Seleccione un estanque</option>
          <option v-for="e in estanques" :key="e.id_estanque" :value="e.id_estanque">{{ e.nombre }}</option>
        </select>
      </div>

      <div class="form-group">
        <label for="ciclo">Ciclo:</label>
        <select v-model="siembraSeleccionada" id="ciclo" required>
          <option disabled value="">Seleccione un ciclo</option>
          <option v-for="c in ciclos" :key="c.id_siembra" :value="c.id_siembra">{{ formatDate(c.fecha) }} - {{ c.especie }}</option>
        </select>
      </div>

      <div class="form-group">
        <label for="tipo">Tipo de Análisis:</label>
        <select v-model="tipoSeleccionado" id="tipo" required>
          <option value="Crecimiento">Crecimiento</option>
          <option value="Calidad Agua">Calidad Agua</option>
        </select>
      </div>

      <div class="form-group">
        <label for="campo">{{ tipoSeleccionado === 'Crecimiento' ? 'Rubro' : 'Parámetro' }}:</label>
        <select v-model="campoSeleccionado" id="campo" required>
          <option disabled value="">Seleccione una opción</option>
          <option v-for="c in camposDisponibles" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <button type="submit">Aplicar Prueba</button>
    </form>

    <div v-if="resultado">
      <h3>Resultado de la Prueba Shapiro-Wilk</h3>
      <p><strong>Estadístico W:</strong> {{ resultado.w.toFixed(4) }}</p>
      <p><strong>Valor p:</strong> {{ resultado.p.toFixed(4) }}</p>
      <p><strong>Conclusión:</strong> 
        <span :style="{ color: resultado.p < 0.05 ? 'red' : 'green' }">
          {{ resultado.p < 0.05 ? 'No se distribuye normalmente' : 'Distribución normal aceptada' }}
        </span>
      </p>
      <button @click="generarPDF">Exportar PDF</button>
      <button @click="exportarExcel">Exportar Excel</button>
    </div>
  </div>
  <canvas id="grafico-shapiro" width="600" height="300" style="display: none;"></canvas>
</template>

<script>
import axios from "@/services/axios";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import * as XLSX from "xlsx";
import Chart from "chart.js/auto";
import { logoBase64 } from "@/utils/logo"; 

export default {
  name: "ShapiroWilk",
  data() {
    return {
      estanques: [],
      ciclos: [],
      camposDisponibles: [],
      datos: [],
      tipoSeleccionado: "Crecimiento",
      estanqueSeleccionado: "",
      siembraSeleccionada: "",
      campoSeleccionado: "",
      resultado: null
    };
  },
  methods: {
    formatDate(fecha) {
      return new Date(fecha).toISOString().split("T")[0];
    },
    async obtenerEstanques() {
      const user = JSON.parse(localStorage.getItem("user"));
      const res = await axios.get("/estanque/");
      this.estanques = res.data.filter(e => e.estatus && e.acuicola === user.acuicola);
    },
    async obtenerCiclos() {
      const res = await axios.get("/siembra/");
      this.ciclos = res.data.filter(s => s.estanque === this.estanqueSeleccionado);
    },
    async obtenerCampos() {
      this.camposDisponibles = [];

      if (this.tipoSeleccionado === "Crecimiento") {
        const [crecimientos, rubros] = await Promise.all([
          axios.get("/crecimiento/"),
          axios.get("/rubro/")
        ]);
        const usados = crecimientos.data.filter(d => d.siembra === this.siembraSeleccionada);
        const unicos = [...new Set(usados.map(d => d.rubro))];
        this.camposDisponibles = unicos.map(id => {
          const rub = rubros.data.find(r => r.id_rubro === id);
          return rub ? `${rub.nombre} (${rub.unidad})` : null;
        }).filter(Boolean);
      } else {
        this.camposDisponibles = [
          "Temperatura", "Oxígeno disuelto", "pH", "Nitritos", "Nitratos",
          "Sulfato", "Fosfato", "Cloro", "Salinidad"
        ];
      }
    },
    async ejecutarPrueba() {
      if (this.tipoSeleccionado === "Crecimiento") {
        const [crecimientos, rubros] = await Promise.all([
          axios.get("/crecimiento/"),
          axios.get("/rubro/")
        ]);
        const rubro = rubros.data.find(r => this.campoSeleccionado.includes(r.nombre));
        const registros = crecimientos.data.filter(
          d => d.siembra === this.siembraSeleccionada && d.rubro === rubro.id_rubro
        );
        this.datos = registros.map(r => ({
          fecha: r.fecha,
          valor: r.medicion
        }));
      } else {
        const map = {
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
        const field = map[this.campoSeleccionado];
        const res = await axios.get("/calidad-agua/");
        const registros = res.data.filter(d => d.siembra === this.siembraSeleccionada && d[field] !== null);
        this.datos = registros.map(d => ({
          fecha: d.fecha,
          valor: d[field]
        }));
      }

      if (this.datos.length < 3) {
        alert("Se requieren al menos 3 datos para aplicar la prueba.");
        return;
      }
      const valores = this.datos.map(d => d.valor);
      const sorted = [...valores].sort((a, b) => a - b);
      const n = sorted.length;
      const mean = valores.reduce((a, b) => a + b, 0) / n;
      const ssd = valores.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0);
      const a = Math.sqrt((n - 1) / n);
      const num = Math.pow(a * (sorted[n - 1] - sorted[0]), 2);
      const W = num / ssd;
      const p = 1 - W;
      this.resultado = { w: W, p };
    },
    async generarPDF() {
      const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "letter" });
      const tipo = this.tipoSeleccionado;
      const campo = this.campoSeleccionado;
      const fechaGeneracion = new Date().toLocaleString("es-MX");

      // Logotipo
      doc.addImage(logoBase64, "PNG", 160, 10, 40, 15);

      // Encabezado
      doc.setFontSize(16);
      doc.text("Prueba de Normalidad Shapiro-Wilk", 14, 20);

      doc.setFontSize(12);
      const info = [
        `Estanque: ${this.estanqueSeleccionado}`,
        `Ciclo: ${this.siembraSeleccionada}`,
        `Tipo: ${tipo}`,
        `${tipo === "Crecimiento" ? "Rubro" : "Parámetro"}: ${campo}`,
        `Estadístico W: ${this.resultado.w.toFixed(4)}`,
        `Valor p: ${this.resultado.p.toFixed(4)}`,
        `Conclusión: ${this.resultado.p < 0.05
          ? "Los datos no provienen de una distribución normal (se rechaza H0)"
          : "No se rechaza la hipótesis de normalidad (distribución normal aceptada)"}`
      ];

      info.forEach((linea, i) => {
        doc.text(linea, 14, 30 + i * 7);
      });

      // Tabla de datos
      const data = this.datos.map((d, i) => [
        i + 1,
        new Date(d.fecha).toISOString().split("T")[0],
        d.valor
      ]);

      autoTable(doc, {
        startY: 30 + info.length * 7 + 10,
        head: [["#", "Fecha", "Valor"]],
        body: data,
        styles: {
          fontSize: 10,
          cellPadding: 3,
          halign: "center"
        },
        columnStyles: {
          1: { cellWidth: 30, textDirection: 90 }
        },
        headStyles: {
          fillColor: [40, 167, 69],
          textColor: 255,
          fontStyle: 'bold'
        },
        didDrawPage: function (data) {
          const pageHeight = doc.internal.pageSize.getHeight();
          doc.setFontSize(10);
          doc.setTextColor(150);
          doc.text(`Módulo: Shapiro-Wilk | Generado: ${fechaGeneracion}`, 14, pageHeight - 15);
        },
        pageBreak: 'auto'
      });

      // Gráfico
      await this.generarGraficoPDF("bar");
      const canvas = document.getElementById("grafico-shapiro");
      const imgData = canvas.toDataURL("image/png");
      const finalY = doc.lastAutoTable.finalY + 10;
      const imgWidth = 160;
      const imgHeight = 90;
      const pageHeight = doc.internal.pageSize.getHeight();
      const pageWidth = doc.internal.pageSize.getWidth();
      const imgX = (pageWidth - imgWidth) / 2;

      if (finalY + imgHeight > pageHeight - 20) {
        doc.addPage();
        doc.setFontSize(10);
        doc.setTextColor(150);
        doc.text(`Módulo: Shapiro-Wilk | Generado: ${fechaGeneracion}`, 14, pageHeight - 15);

        doc.setFontSize(13);
        doc.setTextColor(0);
        doc.text("Gráfico de valores del parámetro", imgX, 20);

        doc.addImage(imgData, "PNG", imgX, 30, imgWidth, imgHeight);
      } else {
        doc.setFontSize(13);
        doc.setTextColor(0);
        doc.text("Gráfico de valores del parámetro", imgX, finalY);

        doc.addImage(imgData, "PNG", imgX, finalY + 5, imgWidth, imgHeight);
      }

      const nombre = `shapiro_wilk_${tipo}_${campo.replace(/\s+/g, "_")}_${Date.now()}.pdf`;
      doc.save(nombre);
    },
    async generarGraficoPDF(tipo = "bar") {
      return new Promise((resolve) => {
        const ctx = document.getElementById("grafico-shapiro").getContext("2d");

        if (this.chartInstance) {
          this.chartInstance.destroy();
        }

        this.chartInstance = new Chart(ctx, {
          type: tipo,
          data: {
            labels: this.datos.map(d => new Date(d.fecha).toISOString().split("T")[0]),
            datasets: [{
              label: "Valores",
              data: this.datos.map(d => d.valor),
              backgroundColor: "rgba(75, 192, 192, 0.4)",
              borderColor: "rgba(75, 192, 192, 1)",
              borderWidth: 1
            }]
          },
          options: {
            responsive: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              x: {
                title: { display: true, text: "Fecha" },
                ticks: {
                  maxRotation: 90,
                  minRotation: 90
                }
              },
              y: {
                title: { display: true, text: "Valor" }
              }
            }
          }
        });

        setTimeout(() => resolve(), 600);
      });
    },
    exportarExcel() {
      const headers = [["#", "Fecha", "Valor"]];
      const rows = this.datos.map((d, i) => [i + 1, d.fecha, d.valor]);

      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.aoa_to_sheet([...headers, ...rows]);
      XLSX.utils.book_append_sheet(wb, ws, "Datos");

      const nombre = `shapiro_datos_${this.tipoSeleccionado}_${this.campoSeleccionado.replace(/\s+/g, "_")}_${Date.now()}.xlsx`;
      XLSX.writeFile(wb, nombre);
    },
  },
  watch: {
    estanqueSeleccionado() {
      this.obtenerCiclos();
    },
    siembraSeleccionada() {
      this.obtenerCampos();
    },
    tipoSeleccionado() {
      this.obtenerCampos();
    }
  },
  mounted() {
    this.obtenerEstanques();
  }
};
</script>

<style scoped>
.grafico-container {
  max-width: auto;
  margin: auto;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.form-group {
  margin-bottom: 16px;
}
select, button {
  padding: 10px;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 6px;
}
button {
  background: #28a745;
  color: white;
  font-weight: bold;
  margin-top: 10px;
}
button:hover {
  background: #218838;
}
.botones {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}
.botones button {
  flex: 1;
}
</style>
