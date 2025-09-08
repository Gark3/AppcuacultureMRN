<template>
  <div class="grafico-container">
    <h1>ANOVA de un Factor</h1>

    <form class="form-seleccion" @submit.prevent="ejecutarANOVA">
      <div class="form-group">
        <label>Tipo de Análisis:</label>
        <select v-model="tipoSeleccionado" required>
          <option value="Crecimiento">Crecimiento</option>
          <option value="Calidad Agua">Calidad Agua</option>
        </select>
      </div>

      <div class="form-group">
        <label>Estanques a comparar:</label>
        <div class="multi-select">
          <label v-for="e in estanques" :key="e.id_estanque">
            <input type="checkbox" :value="e.id_estanque" v-model="estanquesSeleccionados" />
            {{ e.nombre }}
          </label>
        </div>
      </div>

      <div class="form-group">
        <label>{{ tipoSeleccionado === 'Crecimiento' ? 'Rubro' : 'Parámetro' }}:</label>
        <select v-model="campoSeleccionado" required>
          <option disabled value="">Seleccione una opción</option>
          <option v-for="c in camposDisponibles" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <button type="submit">Aplicar ANOVA</button>
    </form>

    <div v-if="resultado">
      <h3>Resultado ANOVA</h3>
      <p><strong>F:</strong> {{ resultado.F.toFixed(4) }}</p>
      <p><strong>Valor p:</strong> {{ resultado.p.toFixed(4) }}</p>
      <p><strong>Conclusión:</strong>
        <span :style="{ color: resultado.p < 0.05 ? 'red' : 'green' }">
          {{ resultado.p < 0.05 ? 'Diferencias significativas entre grupos' : 'No hay diferencias significativas' }}
        </span>
      </p>
      <button @click="generarPDF">Exportar PDF</button>
      <button @click="exportarExcel">Exportar Excel</button>
    </div>
  </div>
  <canvas id="grafico-anova" width="600" height="300" style="display: none;"></canvas>
</template>

<script>
import axios from "@/services/axios";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import * as XLSX from "xlsx";
import Chart from "chart.js/auto";
import { logoBase64 } from "@/utils/logo";

export default {
  name: "Anova",
  data() {
    return {
      tipoSeleccionado: "Crecimiento",
      estanques: [],
      estanquesSeleccionados: [],
      camposDisponibles: [],
      campoSeleccionado: "",
      datosAgrupados: {},
      resultado: null,
      chartInstance: null
    };
  },
  methods: {
    async obtenerEstanques() {
      const user = JSON.parse(localStorage.getItem("user"));
      const res = await axios.get("/estanque/");
      this.estanques = res.data.filter(e => e.estatus && e.acuicola === user.acuicola);
    },
    async obtenerCampos() {
      if (this.tipoSeleccionado === "Crecimiento") {
        const rubros = await axios.get("/rubro/");
        this.camposDisponibles = rubros.data.map(r => `${r.nombre} (${r.unidad})`);
      } else {
        this.camposDisponibles = [
          "Temperatura", "Oxígeno disuelto", "pH", "Nitritos", "Nitratos",
          "Sulfato", "Fosfato", "Cloro", "Salinidad"
        ];
      }
    },
    async ejecutarANOVA() {
      const campo = this.campoSeleccionado;
      this.datosAgrupados = {};

      for (const id of this.estanquesSeleccionados) {
        const siembras = await axios.get("/siembra/");
        const activas = siembras.data.filter(s => s.estanque === id && !s.fecha_cosecha);

        let valores = [];
        for (const siembra of activas) {
          if (this.tipoSeleccionado === "Crecimiento") {
            const [crecimientos, rubros] = await Promise.all([
              axios.get("/crecimiento/"),
              axios.get("/rubro/")
            ]);
            const rubro = rubros.data.find(r => campo.includes(r.nombre));
            const registros = crecimientos.data.filter(
              c => c.siembra === siembra.id_siembra && c.rubro === rubro.id_rubro
            );
            valores.push(...registros.map(r => r.medicion));
          } else {
            const map = {
              "Temperatura": "temperatura",
              "Oxígeno disuelto": "oxigeno_disuelto",
              "pH": "ph", "Nitritos": "nitritos", "Nitratos": "nitratos",
              "Sulfato": "sulfato", "Fosfato": "fosfato",
              "Cloro": "cloro", "Salinidad": "salinidad"
            };
            const param = map[campo];
            const calidad = await axios.get("/calidad-agua/");
            const registros = calidad.data.filter(
              d => d.siembra === siembra.id_siembra && d[param] !== null
            );
            valores.push(...registros.map(d => d[param]));
          }
        }

        if (valores.length > 0) {
          const estanqueNombre = this.estanques.find(e => e.id_estanque === id).nombre;
          this.datosAgrupados[estanqueNombre] = valores;
        }
      }

      this.resultado = this.calcularANOVA(this.datosAgrupados);
      this.$nextTick(() => this.generarGraficoPDF());
    },
    calcularANOVA(grupos) {
      const nombres = Object.keys(grupos);
      const k = nombres.length;
      const n_total = nombres.reduce((sum, key) => sum + grupos[key].length, 0);
      const allData = nombres.flatMap(key => grupos[key]);
      const globalMean = allData.reduce((a, b) => a + b, 0) / n_total;

      const ss_between = nombres.reduce((sum, key) => {
        const group = grupos[key];
        const mean = group.reduce((a, b) => a + b, 0) / group.length;
        return sum + group.length * Math.pow(mean - globalMean, 2);
      }, 0);

      const ss_within = nombres.reduce((sum, key) => {
        const group = grupos[key];
        const mean = group.reduce((a, b) => a + b, 0) / group.length;
        return sum + group.reduce((s, x) => s + Math.pow(x - mean, 2), 0);
      }, 0);

      const df_between = k - 1;
      const df_within = n_total - k;

      const ms_between = ss_between / df_between;
      const ms_within = ss_within / df_within;
      const F = ms_between / ms_within;

      const p = 1 - this.fCdf(F, df_between, df_within); // Estimación rápida

      return { F, p, df_between, df_within, grupos };
    },
    // Función aproximada de distribución F
    fCdf(F, df1, df2) {
      // Aprox rápida, si quieres más precisión usa librerías como jstat
      if (F <= 0) return 0;
      const x = (df1 * F) / (df1 * F + df2);
      return Math.pow(x, df1 / 2);
    },
    exportarExcel() {
      const headers = [["Grupo", "Valor"]];
      const rows = [];
      for (const grupo in this.datosAgrupados) {
        this.datosAgrupados[grupo].forEach(v => rows.push([grupo, v]));
      }
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.aoa_to_sheet([...headers, ...rows]);
      XLSX.utils.book_append_sheet(wb, ws, "ANOVA");
      XLSX.writeFile(wb, `anova_datos_${this.tipoSeleccionado}_${Date.now()}.xlsx`);
    },
    async generarPDF() {
      const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "letter" });
      const fecha = new Date().toLocaleString("es-MX");
      const campo = this.campoSeleccionado;

      doc.addImage(logoBase64, "PNG", 160, 10, 40, 15);
      doc.setFontSize(16);
      doc.text("ANOVA de un Factor", 14, 20);
      doc.setFontSize(12);
      const info = [
        `Tipo: ${this.tipoSeleccionado}`,
        `Rubro/Parámetro: ${campo}`,
        `Grupos: ${Object.keys(this.datosAgrupados).length}`,
        `F: ${this.resultado.F.toFixed(4)}`,
        `Valor p: ${this.resultado.p.toFixed(4)}`,
        `Conclusión: ${this.resultado.p < 0.05 ? "Diferencias significativas" : "No significativas"}`
      ];
      info.forEach((linea, i) => doc.text(linea, 14, 30 + i * 7));

      const rows = [];
      for (const grupo in this.datosAgrupados) {
        this.datosAgrupados[grupo].forEach(v => rows.push([grupo, v]));
      }

      autoTable(doc, {
        startY: 30 + info.length * 7 + 10,
        head: [["Grupo", "Valor"]],
        body: rows,
        styles: { fontSize: 10, halign: "center" },
        headStyles: {
          fillColor: [40, 167, 69],
          textColor: 255,
          fontStyle: "bold"
        },
        didDrawPage: () => {
          const h = doc.internal.pageSize.getHeight();
          doc.setFontSize(10);
          doc.setTextColor(150);
          doc.text(`Módulo: ANOVA | Generado: ${fecha}`, 14, h - 15);
        },
        pageBreak: 'auto'
      });

      await this.generarGraficoPDF();
      const canvas = document.getElementById("grafico-anova");
      const img = canvas.toDataURL("image/png");
      const finalY = doc.lastAutoTable.finalY + 10;
      const imgW = 160, imgH = 90;
      const pageH = doc.internal.pageSize.getHeight();
      const pageW = doc.internal.pageSize.getWidth();
      const imgX = (pageW - imgW) / 2;

      if (finalY + imgH > pageH - 20) {
        doc.addPage();
        doc.setFontSize(13);
        doc.setTextColor(0);
        doc.text("Gráfico comparativo de grupos", imgX, 20);
        doc.addImage(img, "PNG", imgX, 30, imgW, imgH);
      } else {
        doc.setFontSize(13);
        doc.setTextColor(0);
        doc.text("Gráfico comparativo de grupos", imgX, finalY);
        doc.addImage(img, "PNG", imgX, finalY + 5, imgW, imgH);
      }

      doc.save(`anova_${this.tipoSeleccionado}_${campo.replace(/\s+/g, "_")}_${Date.now()}.pdf`);
    },
    async generarGraficoPDF() {
      return new Promise(resolve => {
        const ctx = document.getElementById("grafico-anova").getContext("2d");
        if (this.chartInstance) this.chartInstance.destroy();

        this.chartInstance = new Chart(ctx, {
          type: "bar",
          data: {
            labels: Object.keys(this.datosAgrupados),
            datasets: [{
              label: "Promedio",
              data: Object.values(this.datosAgrupados).map(arr => arr.reduce((a, b) => a + b, 0) / arr.length),
              backgroundColor: "rgba(75, 192, 192, 0.4)",
              borderColor: "rgba(75, 192, 192, 1)",
              borderWidth: 1
            }]
          },
          options: {
            responsive: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { title: { display: true, text: "Grupo (Estanque)" }},
              y: { title: { display: true, text: "Promedio del parámetro" }}
            }
          }
        });

        setTimeout(() => resolve(), 600);
      });
    }
  },
  watch: {
    tipoSeleccionado() {
      this.obtenerCampos();
    }
  },
  mounted() {
    this.obtenerEstanques();
    this.obtenerCampos();
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
.multi-select {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 5px;
}
.multi-select label {
  display: block;
  margin: 5px 0;
}
</style>
