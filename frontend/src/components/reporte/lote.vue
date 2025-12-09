<template>
  <div class="reporte-salidas-container">
    <h1>Reporte de salidas de almacén</h1>

    <!-- FILTROS DE FECHA -->
    <form class="filtros" @submit.prevent="aplicarFiltros">
      <div class="card filtros-card">
        <div class="form-row">
          <div class="form-group">
            <label for="fechaInicio">Fecha inicio</label>
            <input
              id="fechaInicio"
              type="date"
              v-model="filtros.fechaInicio"
              required
            />
          </div>
          <div class="form-group">
            <label for="fechaFin">Fecha fin</label>
            <input
              id="fechaFin"
              type="date"
              v-model="filtros.fechaFin"
              required
            />
          </div>
        </div>

        <div class="form-row acciones">
          <button type="submit" class="btn-cta" :disabled="cargando">
            Aplicar filtros
          </button>
          <button
            type="button"
            class="btn-sm outline"
            @click="limpiarFiltros"
            :disabled="cargando"
          >
            Limpiar
          </button>
        </div>
      </div>
    </form>

    <!-- MENSAJES DE ESTADO -->
    <div v-if="error" class="alert error">
      {{ error }}
    </div>
    <div v-if="cargando" class="alert">
      Cargando datos de salidas…
    </div>

    <!-- SIN DATOS -->
    <div
      v-if="!cargando && !error && registrosFiltrados.length === 0 && rangoTexto"
      class="muted"
    >
      No hay salidas para el rango seleccionado.
    </div>

    <!-- TABLA Y RESUMEN -->
    <div v-else-if="registrosFiltrados.length">
      <div class="resumen">
        <h2>Resumen</h2>
        <p><strong>Acuícola:</strong> {{ farmName }}</p>
        <p v-if="rangoTexto">
          <strong>Periodo:</strong> {{ rangoTexto }}
        </p>
        <p><strong>Total de salidas unitarias:</strong> {{ registrosFiltrados.length }}</p>
        <p><strong>Monto total estimado:</strong> ${{ totalMonto.toFixed(2) }}</p>
      </div>

      <div class="tabla-wrapper">
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>ID salida</th>
              <th>ID salida unitaria</th>
              <th>Producto</th>
              <th>Lote</th>
              <th>Cant.</th>
              <th>Kg</th>
              <th>Costo estimado</th>
              <th>Siembra</th>
              <th>Solicitó</th>
              <th>Registró</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in registrosFiltrados" :key="row.id_salida_unitaria">
              <td>{{ formatearFechaHora(row.fechaIso) }}</td>
              <td>{{ row.id_salida }}</td>
              <td>{{ row.id_salida_unitaria }}</td>
              <td>{{ row.producto }}</td>
              <td>{{ row.lote }}</td>
              <td>
                <span v-if="row.cantidad != null">
                  {{ row.cantidad.toFixed(2) }}
                </span>
                <span v-else>-</span>
              </td>
              <td>
                <span v-if="row.cantidad_kg != null">
                  {{ row.cantidad_kg.toFixed(2) }}
                </span>
                <span v-else>-</span>
              </td>
              <td>
                <span v-if="row.costo_salida != null">
                  ${{ row.costo_salida.toFixed(2) }}
                </span>
                <span v-else>-</span>
              </td>
              <td>
                <span v-if="row.siembra_id">
                  {{ row.siembra_id }} — {{ row.siembra_nombre }}
                </span>
                <span v-else>-</span>
              </td>
              <td>{{ row.solicitante || '-' }}</td>
              <td>{{ row.registrado_por || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- BOTONES PDF -->
      <div class="btn-row">
        <button
          type="button"
          class="btn-generar outline"
          @click="mostrarVistaPrevia"
          :disabled="cargando || !registrosFiltrados.length"
        >
          Vista previa PDF
        </button>
        <button
          type="button"
          class="btn-generar"
          @click="exportarReporte"
          :disabled="cargando || !registrosFiltrados.length"
        >
          Descargar PDF
        </button>
      </div>
    </div>

    <!-- MODAL PREVIEW PDF -->
    <div v-if="showPreview" class="modal-overlay" @click.self="cerrarPreview">
      <div class="modal">
        <div class="modal-header">
          <strong>Vista previa del reporte</strong>
          <button class="btn-sm outline" @click="cerrarPreview">Cerrar</button>
        </div>
        <iframe :src="previewUrl" class="pdf-frame"></iframe>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import axios from "@/services/axios";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

// Lee nombre de la granja desde localStorage (igual que en otros reportes)
const readFarmNameFromStorage = () => {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    const raw =
      user.acuicolaNombre ??
      user.acuicola_name ??
      user.acuicola ??
      user.empresa ??
      "Granja Acuícola";
    return String(raw);
  } catch {
    return "Granja Acuícola";
  }
};

// Lee nombre del usuario actual (para el encabezado del reporte)
const readUserNameFromStorage = () => {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    return String(user.nombre || user.username || "Usuario");
  } catch {
    return "Usuario";
  }
};

const pad2 = (n) => String(n).padStart(2, "0");

const formatFechaCorta = (value) => {
  const d = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return `${pad2(d.getDate())}/${pad2(d.getMonth() + 1)}/${d.getFullYear()}`;
};

export default {
  name: "ReporteSalidasLote",
  setup() {
    const filtros = ref({
      fechaInicio: "",
      fechaFin: "",
    });

    // Rango aplicado (ya validado)
    const rango = ref({
      inicio: null,
      fin: null,
    });

    const cargando = ref(false);
    const error = ref("");

    const farmName = ref(readFarmNameFromStorage());
    const currentUserName = ref(readUserNameFromStorage());

    // Datos base
    const salidas = ref([]); // /salida/
    const salidasUnitarias = ref([]); // /salida-unitaria/
    const salidasEstanques = ref([]); // /salida-estanque/
    const siembras = ref([]); // /siembra/
    const estanques = ref([]); // /estanque/
    const productos = ref([]); // /producto/
    const perfiles = ref([]); // /perfiles/
    const entradasUnitarias = ref([]); // /entrada-unitaria/

    // PDF preview
    const showPreview = ref(false);
    const previewUrl = ref(null);

    const formatearFechaHora = (isoStr) => {
      if (!isoStr) return "";
      const d = new Date(isoStr);
      if (Number.isNaN(d.getTime())) return isoStr;
      return `${pad2(d.getDate())}/${pad2(d.getMonth() + 1)}/${d.getFullYear()} ${pad2(
        d.getHours()
      )}:${pad2(d.getMinutes())}`;
    };

    const rangoTexto = computed(() => {
      if (!rango.value.inicio || !rango.value.fin) return "";
      return `${formatFechaCorta(rango.value.inicio)} al ${formatFechaCorta(
        rango.value.fin
      )}`;
    });

    // Carga inicial de datos
    const cargarDatos = async () => {
      try {
        cargando.value = true;
        error.value = "";

        const [
          resSalidas,
          resSalidasUnitarias,
          resSalidasEstanques,
          resSiembras,
          resEstanques,
          resProductos,
          resPerfiles,
          resEntradasUnitarias,
        ] = await Promise.all([
          axios.get("/salida/"),
          axios.get("/salida-unitaria/"),
          axios.get("/salida-estanque/"),
          axios.get("/siembra/"),
          axios.get("/estanque/"),
          axios.get("/producto/"),
          axios.get("/perfiles/"),
          axios.get("/entrada-unitaria/"),
        ]);

        salidas.value = resSalidas.data || [];
        salidasUnitarias.value = resSalidasUnitarias.data || [];
        salidasEstanques.value = resSalidasEstanques.data || [];
        siembras.value = resSiembras.data || [];
        estanques.value = resEstanques.data || [];
        productos.value = resProductos.data || [];
        perfiles.value = resPerfiles.data || [];
        entradasUnitarias.value = resEntradasUnitarias.data || [];
      } catch (e) {
        console.error(e);
        error.value = "Ocurrió un error al cargar los datos de salidas.";
      } finally {
        cargando.value = false;
      }
    };

    onMounted(() => {
      cargarDatos();
    });

    // Validar y aplicar rango de fechas
    const aplicarFiltros = () => {
      error.value = "";

      if (!filtros.value.fechaInicio || !filtros.value.fechaFin) {
        error.value = "Selecciona la fecha de inicio y la fecha de fin.";
        return;
      }

      const ini = new Date(`${filtros.value.fechaInicio}T00:00:00`);
      const fin = new Date(`${filtros.value.fechaFin}T23:59:59`);

      if (Number.isNaN(ini.getTime()) || Number.isNaN(fin.getTime())) {
        error.value = "Las fechas seleccionadas no son válidas.";
        return;
      }

      if (ini > fin) {
        error.value = "La fecha de inicio no puede ser mayor que la fecha de fin.";
        return;
      }

      rango.value = { inicio: ini, fin: fin };
    };

    const limpiarFiltros = () => {
      filtros.value.fechaInicio = "";
      filtros.value.fechaFin = "";
      rango.value = { inicio: null, fin: null };
      error.value = "";
    };

    // Registros del reporte (con joins y cálculos)
    const registrosFiltrados = computed(() => {
      if (!rango.value.inicio || !rango.value.fin) return [];

      const rows = [];

      // Maps auxiliares
      const mapSalidaById = new Map();
      salidas.value.forEach((s) => {
        mapSalidaById.set(s.id_salida_producto, s);
      });

      const mapProducto = new Map();
      productos.value.forEach((p) => {
        mapProducto.set(p.id_producto, p);
      });

      const mapSiembra = new Map();
      siembras.value.forEach((s) => {
        mapSiembra.set(s.id_siembra, s);
      });

      const mapEstanque = new Map();
      estanques.value.forEach((e) => {
        mapEstanque.set(e.id_estanque, e);
      });

      const mapSalidaEstanqueBySalidaUnit = new Map();
      salidasEstanques.value.forEach((se) => {
        // campo viene como id de salidaunitaria
        mapSalidaEstanqueBySalidaUnit.set(se.salidaunitaria, se.siembra);
      });

      // Perfiles: por user.id y por perfil.id
      const mapPerfilByUserId = new Map();
      const mapPerfilByPerfilId = new Map();
      perfiles.value.forEach((p) => {
        mapPerfilByUserId.set(p.user.id, p);
        mapPerfilByPerfilId.set(p.id, p);
      });

      const nombreUsuarioPorId = (userId) => {
        if (userId == null) return "";
        const perfil = mapPerfilByUserId.get(userId);
        if (perfil && perfil.user) {
          return perfil.user.username || `Usuario ${perfil.user.id}`;
        }
        return `ID ${userId}`;
      };

      const nombreSolicitantePorId = (id) => {
        if (id == null) return "";
        const perfil =
          mapPerfilByPerfilId.get(id) || mapPerfilByUserId.get(id);
        if (perfil && perfil.user) {
          return perfil.user.username || `Usuario ${perfil.user.id}`;
        }
        return `ID ${id}`;
      };

      // Costo promedio por producto+lote usando las entradas unitarias
      const acumPorClave = new Map();
      entradasUnitarias.value.forEach((e) => {
        const key = `${e.producto}|${e.lote}`;
        let acc = acumPorClave.get(key);
        if (!acc) {
          acc = { kg: 0, costo: 0 };
          acumPorClave.set(key, acc);
        }
        acc.kg += e.cantidad_kg || 0;
        acc.costo += e.costo || 0;
      });

      const costoPorKg = new Map();
      acumPorClave.forEach((acc, key) => {
        if (acc.kg > 0) {
          costoPorKg.set(key, acc.costo / acc.kg);
        }
      });

      salidasUnitarias.value.forEach((su) => {
        const fechaRegistro = new Date(su.fecha);
        if (
          fechaRegistro < rango.value.inicio ||
          fechaRegistro > rango.value.fin
        ) {
          return;
        }

        const salida = mapSalidaById.get(su.salida);
        const producto = mapProducto.get(su.producto);

        const keyCosto = `${su.producto}|${su.lote}`;
        const costoKg = costoPorKg.get(keyCosto) ?? null;
        const costoSalida =
          costoKg != null && su.cantidad_kg != null
            ? costoKg * su.cantidad_kg
            : null;

        const siembraId =
          mapSalidaEstanqueBySalidaUnit.get(su.id_salida_unitaria) || null;
        const siembra = siembraId ? mapSiembra.get(siembraId) : null;
        const estanque = siembra ? mapEstanque.get(siembra.estanque) : null;

        const siembraNombre = siembra
          ? `${siembra.especie}${
              estanque ? " — " + estanque.nombre : ""
            }`
          : "";

        rows.push({
          fechaIso: su.fecha,
          fecha: fechaRegistro,
          id_salida: salida ? salida.id_salida_producto : null,
          id_salida_unitaria: su.id_salida_unitaria,
          producto: producto ? producto.nombre : `Producto ${su.producto}`,
          lote: su.lote,
          cantidad: su.cantidad,
          cantidad_kg: su.cantidad_kg,
          costo_salida: costoSalida,
          siembra_id: siembraId,
          siembra_nombre: siembraNombre,
          registrado_por: nombreUsuarioPorId(su.usuario),
          solicitante: salida ? nombreSolicitantePorId(salida.solicitante) : "",
        });
      });

      rows.sort((a, b) => {
        const t = a.fecha - b.fecha;
        if (t !== 0) return t;
        return (a.id_salida_unitaria || 0) - (b.id_salida_unitaria || 0);
      });

      return rows;
    });

    const totalMonto = computed(() =>
      registrosFiltrados.value.reduce(
        (acc, r) => acc + (r.costo_salida || 0),
        0
      )
    );

    const asegurarRango = () => {
      // Si aún no se ha aplicado, pero hay fechas en filtros, intenta aplicarlos
      if (!rango.value.inicio && filtros.value.fechaInicio && filtros.value.fechaFin) {
        aplicarFiltros();
      }
    };

    // ===== PDF (ahora en horizontal y con saltos de línea) =====
    const construirPDF = async ({ preview = false } = {}) => {
      asegurarRango();
      const registros = registrosFiltrados.value;

      // Hoja A4 horizontal en milímetros
      const doc = new jsPDF({
        orientation: "landscape",
        unit: "mm",
        format: "a4",
      });

      const marginLeft = 10;
      const marginRight = 10;
      const marginTop = 18;
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const contentWidth = pageWidth - marginLeft - marginRight;

      const setFont = (font = "helvetica", size = 9, style = "normal") => {
        doc.setFont(font, style);
        doc.setFontSize(size);
      };

      const drawHeader = (page) => {
        doc.setPage(page);
        setFont("helvetica", 11, "bold");
        const title = String(farmName.value || "Granja Acuícola");
        doc.text(title, pageWidth / 2, marginTop - 6, { align: "center" });
        doc.setDrawColor(230);
        doc.line(
          marginLeft,
          marginTop - 4,
          pageWidth - marginRight,
          marginTop - 4
        );
      };

      const ahora = new Date();
      const fechaGeneracion = `${ahora.getFullYear()}-${pad2(
        ahora.getMonth() + 1
      )}-${pad2(ahora.getDate())}`;

      let y = marginTop + 4;

      // Título principal
      setFont("helvetica", 16, "bold");
      doc.text("Reporte de salidas de almacén", marginLeft, y);
      setFont("helvetica", 9);
      doc.setTextColor(120);
      doc.text(`Generado: ${fechaGeneracion}`, pageWidth - marginRight, y, {
        align: "right",
      });
      doc.setTextColor(0);
      y += 8;

      // Resumen principal
      setFont("helvetica", 11, "bold");
      doc.text("Resumen del reporte", marginLeft, y);
      y += 7;

      setFont("helvetica", 9);
      const lineasResumen = [];

      lineasResumen.push(`Acuícola: ${farmName.value}`);
      if (rango.value.inicio && rango.value.fin) {
        lineasResumen.push(
          `Periodo de salidas: ${formatFechaCorta(
            rango.value.inicio
          )} al ${formatFechaCorta(rango.value.fin)}`
        );
      }
      lineasResumen.push(`Generado por: ${currentUserName.value}`);
      lineasResumen.push(`Total de salidas unitarias: ${registros.length}`);
      lineasResumen.push(
        `Monto total estimado: $${totalMonto.value.toFixed(2)}`
      );

      lineasResumen.forEach((txt) => {
        const wrapped = doc.splitTextToSize(txt, contentWidth);
        doc.text(wrapped, marginLeft, y);
        y += 5;
      });
      y += 4;

      // Datos de la tabla
      const body = registros.map((r) => [
        formatearFechaHora(r.fechaIso),
        r.id_salida ?? "",
        r.id_salida_unitaria ?? "",
        r.producto || "",
        r.lote || "",
        r.cantidad != null ? r.cantidad.toFixed(2) : "",
        r.cantidad_kg != null ? r.cantidad_kg.toFixed(2) : "",
        r.costo_salida != null ? r.costo_salida.toFixed(2) : "",
        r.siembra_id
          ? `${r.siembra_id} ${
              r.siembra_nombre ? " - " + r.siembra_nombre : ""
            }`
          : "",
        r.solicitante || "",
        r.registrado_por || "",
      ]);

      autoTable(doc, {
        startY: y,
        margin: { left: marginLeft, right: marginRight, top: marginTop },
        styles: {
          font: "helvetica",
          fontSize: 8,
          cellPadding: 1.5,
          overflow: "linebreak", // rompe en varias líneas
          cellWidth: "wrap",      // ajusta al ancho de la celda
        },
        headStyles: {
          fillColor: [40, 167, 69],
          textColor: 255,
          halign: "center",
        },
        bodyStyles: { valign: "top" },
        // Anchos de columna pensados para A4 horizontal
        columnStyles: {
          0: { cellWidth: 25 }, // Fecha
          1: { cellWidth: 18 }, // ID salida
          2: { cellWidth: 18 }, // ID salida unitaria
          3: { cellWidth: 32 }, // Producto
          4: { cellWidth: 18 }, // Lote
          5: { cellWidth: 18 }, // Cant.
          6: { cellWidth: 18 }, // Kg
          7: { cellWidth: 22 }, // Costo
          8: { cellWidth: 60 }, // Siembra (más ancho)
          9: { cellWidth: 22 }, // Solicitó
          10: { cellWidth: 22 }, // Registró
        },
        head: [
          [
            "Fecha",
            "ID salida",
            "ID U.",
            "Producto",
            "Lote",
            "Cant.",
            "Kg",
            "Costo",
            "Siembra",
            "Solicitó",
            "Registró",
          ],
        ],
        body,
      });

      // Encabezados y pies de página en TODAS las páginas
      const pageCount = doc.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        drawHeader(i);
        doc.setPage(i);
        setFont("helvetica", 8);
        doc.setTextColor(120);
        doc.text(
          `Página ${i} de ${pageCount}`,
          pageWidth / 2,
          pageHeight - 6,
          { align: "center" }
        );
        doc.setTextColor(0);
      }

      if (preview) {
        const blob = doc.output("blob");
        if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
        const url = URL.createObjectURL(blob);
        return url;
      } else {
        doc.save(`reporte_salidas_${Date.now()}.pdf`);
        return null;
      }
    };

    const mostrarVistaPrevia = async () => {
      const url = await construirPDF({ preview: true });
      if (url) {
        previewUrl.value = url;
        showPreview.value = true;
      }
    };

    const cerrarPreview = () => {
      showPreview.value = false;
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value);
        previewUrl.value = null;
      }
    };

    const exportarReporte = async () => {
      await construirPDF({ preview: false });
    };

    return {
      // estado
      filtros,
      cargando,
      error,
      farmName,
      registrosFiltrados,
      totalMonto,
      rangoTexto,

      // acciones
      aplicarFiltros,
      limpiarFiltros,

      // util
      formatearFechaHora,

      // pdf / preview
      showPreview,
      previewUrl,
      mostrarVistaPrevia,
      cerrarPreview,
      exportarReporte,
    };
  },
};
</script>

<style scoped>
.reporte-salidas-container {
  font-family: "Poppins", sans-serif;
  max-width: 1200px;
  margin: 30px auto;
  padding: 24px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
}

h1 {
  font-size: 22px;
  margin-bottom: 18px;
  color: #333;
}

.filtros {
  margin-bottom: 16px;
}

.card {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 16px;
  background: #fafafa;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.form-row.acciones {
  margin-top: 12px;
  justify-content: flex-end;
}

.form-group {
  flex: 1 1 180px;
  display: flex;
  flex-direction: column;
}

label {
  font-weight: 600;
  margin-bottom: 4px;
  color: #444;
  font-size: 14px;
}

input[type="date"] {
  width: 100%;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.15s ease-in-out;
}

input[type="date"]:focus {
  border-color: #28a745;
  outline: none;
  box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.15);
}

/* Botones */
button {
  cursor: pointer;
  transition: transform 0.1s ease-in-out, box-shadow 0.1s ease-in-out;
}

button:hover:not(:disabled) {
  transform: scale(1.02);
}

button:active:not(:disabled) {
  transform: scale(0.98);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cta {
  background: #28a745;
  color: #fff;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 2px 6px rgba(40, 167, 69, 0.3);
}

.btn-sm {
  background: #28a745;
  color: #fff;
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.btn-sm.outline {
  background: #fff;
  color: #28a745;
  border: 1px solid #28a745;
}

.btn-generar {
  margin-top: 12px;
  background: #28a745;
  color: #fff;
  border: none;
  padding: 12px 18px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 14px;
}

.btn-generar.outline {
  background: #fff;
  color: #28a745;
  border: 1px solid #28a745;
}

/* Resumen */
.resumen {
  margin: 16px 0;
  padding: 14px 16px;
  border-radius: 10px;
  background: #f2fff6;
  border: 1px solid #d2f4de;
  font-size: 14px;
}

.resumen h2 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #256c3a;
}

/* Tabla */
.tabla-wrapper {
  margin-top: 10px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  background: #fff;
}

th,
td {
  padding: 8px;
  border: 1px solid #ddd;
  text-align: center;
}

th {
  background: #28a745;
  color: #fff;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

/* Botones PDF */
.btn-row {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Alertas */
.alert {
  padding: 10px 12px;
  border-radius: 8px;
  background: #f1f5f9;
  border: 1px solid #cbd5f5;
  font-size: 13px;
  margin-bottom: 10px;
}

.alert.error {
  background: #fff5f5;
  border-color: #fecaca;
  color: #b91c1c;
}

.muted {
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

/* Modal preview PDF */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal {
  width: min(1000px, 92vw);
  height: min(85vh, 900px);
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}

.pdf-frame {
  width: 100%;
  height: 100%;
  border: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .reporte-salidas-container {
    padding: 16px;
  }

  .form-row {
    flex-direction: column;
  }

  th,
  td {
    font-size: 12px;
    padding: 6px;
  }
}
</style>
