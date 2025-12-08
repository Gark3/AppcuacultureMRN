<template>
  <section class="reporte-salidas">
    <!-- CARD FILTROS -->
    <div class="card">
      <header class="card__header">
        <h2 class="card__title">Reporte de Salidas de Inventario</h2>
        <p class="card__sub">
          Genera un reporte detallado de las salidas entre dos fechas.
        </p>
      </header>

      <form class="form-filtros" @submit.prevent="cargarReporte">
        <div class="field">
          <label class="label" for="fechaInicio">Fecha de inicio</label>
          <input
            id="fechaInicio"
            type="date"
            class="input"
            v-model="fechaInicio"
            required
          />
        </div>

        <div class="field">
          <label class="label" for="fechaFin">Fecha de fin</label>
          <input
            id="fechaFin"
            type="date"
            class="input"
            v-model="fechaFin"
            required
          />
        </div>

        <div class="field field--actions">
          <button
            type="submit"
            class="btn btn--primary"
            :disabled="loading"
          >
            {{ loading ? 'Cargando…' : 'Generar reporte' }}
          </button>
        </div>
      </form>

      <div class="resumen" v-if="salidasNormalizadas.length">
        <p>
          <strong>Rango:</strong>
          {{ rangoTexto }}
        </p>
        <p>
          <strong>Generado por:</strong>
          {{ userName || 'Usuario actual' }}
        </p>
        <p>
          <strong>Acuícola:</strong>
          {{ farmName || 'Granja Acuícola' }}
        </p>
        <p>
          <strong>Registros:</strong> {{ salidasNormalizadas.length }}
          <span v-if="totalEstimado !== null">
            · <strong>Costo total estimado:</strong> {{ formatMoneda(totalEstimado) }}
          </span>
        </p>
      </div>

      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
    </div>

    <!-- TABLA DE RESULTADOS -->
    <div class="card card--mt">
      <header class="card__header card__header--compact">
        <h3 class="card__title">Detalle de salidas</h3>
      </header>

      <div v-if="!salidasNormalizadas.length && !loading" class="empty-state">
        No hay salidas registradas en el rango seleccionado.
      </div>

      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>ID Salida</th>
              <th>ID Salida Unitaria</th>
              <th>Producto</th>
              <th>Cantidad</th>
              <th>Costo unitario</th>
              <th>Ciclo (siembra)</th>
              <th>Registró</th>
              <th>Solicitante</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in salidasNormalizadas" :key="row.rowKey">
              <td>{{ formatFecha(row.fecha) }}</td>
              <td>{{ row.idSalida ?? '—' }}</td>
              <td>{{ row.idSalidaUnitaria ?? '—' }}</td>
              <td>{{ row.productoNombre || '—' }}</td>
              <td>
                {{ row.cantidad }}
                <span v-if="row.unidad" class="text-muted"> {{ row.unidad }}</span>
              </td>
              <td class="text-right">
                {{ row.costoUnitario != null ? formatMoneda(row.costoUnitario) : '—' }}
              </td>
              <td>
                <span v-if="row.siembraId">
                  #{{ row.siembraId }} — {{ row.siembraNombre || 'Siembra' }}
                </span>
                <span v-else class="text-muted">Sin siembra</span>
              </td>
              <td>{{ row.usuarioRegistro || '—' }}</td>
              <td>{{ row.solicitante || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="btn-row" v-if="salidasNormalizadas.length">
        <button type="button" class="btn btn--outline" @click="mostrarVistaPrevia">
          Vista previa PDF
        </button>
        <button type="button" class="btn btn--primary" @click="exportarPDF">
          Descargar PDF
        </button>
      </div>
    </div>

    <!-- MODAL PREVIEW PDF -->
    <div v-if="showPreview" class="modal-overlay" @click.self="cerrarPreview">
      <div class="modal">
        <div class="modal-header">
          <strong>Vista previa del reporte</strong>
          <button class="btn btn--outline btn--sm" @click="cerrarPreview">Cerrar</button>
        </div>
        <iframe :src="previewUrl" class="pdf-frame"></iframe>
      </div>
    </div>
  </section>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from '@/services/axios';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

function hoyISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function primerDiaMesActualISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}-01`;
}

function readUserContext() {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}');
    const nombre =
      u.nombre_completo ??
      u.nombre ??
      u.full_name ??
      u.username ??
      'Usuario';
    const farm =
      u.acuicolaNombre ??
      u.acuicola_name ??
      u.acuicola ??
      u.empresa ??
      'Granja Acuícola';
    return { nombre: String(nombre), farmName: String(farm), userId: u.usuario_id ?? u.id ?? null };
  } catch {
    return { nombre: 'Usuario', farmName: 'Granja Acuícola', userId: null };
  }
}

export default {
  name: 'ReporteSalidas',
  setup() {
    const { nombre, farmName, userId } = readUserContext();

    const fechaInicio = ref(primerDiaMesActualISO());
    const fechaFin = ref(hoyISO());

    const rawSalidas = ref([]); // respuesta directa del backend
    const loading = ref(false);
    const errorMsg = ref('');

    const userName = ref(nombre);
    const acuicolaName = ref(farmName);
    const currentUserId = ref(userId);

    const showPreview = ref(false);
    const previewUrl = ref(null);

    // Normalizar filas para que la tabla y el PDF no dependan de cómo se llame cada campo.
    const salidasNormalizadas = computed(() => {
      const rows = (rawSalidas.value || []).map((r, idx) => {
        const salidaId =
          r.id_salida ??
          r.salida_id ??
          r.id_salida_producto ??
          r.salida ??
          null;

        const salidaUnitariaId =
          r.id_salida_unitaria ??
          r.salida_unitaria_id ??
          r.salidaunitaria ??
          r.id ??
          null;

        const productoNombre =
          r.producto_nombre ??
          r.nombre_producto ??
          (r.producto && (r.producto.nombre || r.producto.nombre_completo)) ??
          '';

        const unidad =
          r.unidad ??
          r.modo ??
          (r.cantidad_kg != null ? 'kg' : null);

        const cantidad =
          r.cantidad ??
          r.cantidad_salida ??
          r.cantidad_kg ??
          r.cantidad_unidades ??
          0;

        const costoUnit =
          r.costo_salida_unitaria ??
          r.costo_unitario ??
          r.precio_unitario ??
          r.costo ??
          null;

        const fecha =
          r.fecha_salida ??
          r.fecha ??
          r.created_at ??
          r.fecha_registro ??
          null;

        const siembraId =
          (typeof r.siembra === 'object'
            ? (r.siembra.id_siembra ?? r.siembra.id ?? null)
            : (r.siembra_id ?? r.siembra ?? null));

        const siembraNombre =
          r.siembra_nombre ??
          (r.siembra && (r.siembra.nombre || r.siembra.etiqueta || r.siembra.especie)) ??
          null;

        const usuarioRegistro =
          r.usuario_registro_nombre ??
          r.usuario_nombre ??
          (r.usuario && (r.usuario.nombre || r.usuario.username)) ??
          null;

        const solicitante =
          r.solicitante_nombre ??
          (r.solicitante && (r.solicitante.nombre || r.solicitante.username)) ??
          null;

        return {
          rowKey: `${salidaId || 'S'}-${salidaUnitariaId || idx}`,
          idSalida: salidaId,
          idSalidaUnitaria: salidaUnitariaId,
          productoNombre,
          cantidad: Number(cantidad) || 0,
          unidad,
          costoUnitario: costoUnit != null ? Number(costoUnit) : null,
          fecha,
          siembraId,
          siembraNombre,
          usuarioRegistro,
          solicitante,
        };
      });

      // Orden cronológico ascendente
      return rows.sort((a, b) => {
        const ta = a.fecha ? new Date(a.fecha).getTime() : 0;
        const tb = b.fecha ? new Date(b.fecha).getTime() : 0;
        return ta - tb;
      });
    });

    const totalEstimado = computed(() => {
      if (!salidasNormalizadas.value.length) return null;
      let sum = 0;
      for (const r of salidasNormalizadas.value) {
        if (r.costoUnitario != null) {
          sum += r.cantidad * r.costoUnitario;
        }
      }
      return sum;
    });

    const rangoTexto = computed(() => {
      if (!fechaInicio.value || !fechaFin.value) return '—';
      return `${fechaInicio.value} a ${fechaFin.value}`;
    });

    const formatMoneda = (v) => {
      const n = Number(v) || 0;
      return n.toLocaleString('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 2,
      });
    };

    const formatFecha = (f) => {
      if (!f) return '—';
      const d = new Date(f);
      if (Number.isNaN(d.getTime())) return f;
      return d.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      });
    };

    const cargarReporte = async () => {
      errorMsg.value = '';
      rawSalidas.value = [];
      if (!fechaInicio.value || !fechaFin.value) {
        errorMsg.value = 'Selecciona una fecha de inicio y fin.';
        return;
      }
      try {
        loading.value = true;

        // 👇 AJUSTA ESTA RUTA Y NOMBRES DE QUERIES A TU BACKEND
        const { data } = await axios.get('/reporte-salidas/', {
          params: {
            fecha_inicio: fechaInicio.value,
            fecha_fin: fechaFin.value,
            acuicola: acuicolaName.value,
            // si tu backend filtra por id de acuícola, cambia esto a acuicola_id
          },
        });

        // Soportar tanto lista directa como formato paginado
        rawSalidas.value = Array.isArray(data) ? data : (data.results || []);
      } catch (err) {
        console.error('Error al cargar reporte de salidas:', err);
        errorMsg.value = 'Ocurrió un error al consultar el reporte.';
      } finally {
        loading.value = false;
      }
    };

    // ====== PDF ======
    const construirPDF = () => {
      const doc = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' });
      const M = 40;
      const PAGE_W = doc.internal.pageSize.getWidth();
      const PAGE_H = doc.internal.pageSize.getHeight();
      const CONTENT_W = PAGE_W - M * 2;

      const setFont = (size = 10, style = 'normal') => {
        doc.setFont('helvetica', style);
        doc.setFontSize(size);
      };

      // Encabezado principal (solo primera página)
      const now = new Date();
      const fGen = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(
        now.getDate()
      ).padStart(2, '0')}`;

      setFont(14, 'bold');
      doc.text('Reporte de salidas de inventario', M, M + 4);

      setFont(10);
      doc.setTextColor(120);
      doc.text(`Generado: ${fGen}`, PAGE_W - M, M + 4, { align: 'right' });
      doc.setTextColor(0);

      doc.setDrawColor(220);
      doc.line(M, M + 10, PAGE_W - M, M + 10);

      let y = M + 26;

      // Bloque información general
      setFont(11, 'bold');
      doc.text('Información del reporte', M, y);
      y += 14;

      setFont(10);
      const infoLines = [
        `Rango de fechas: ${rangoTexto.value}`,
        `Generado por: ${userName.value}`,
        `Acuícola: ${acuicolaName.value}`,
        `Número de salidas: ${salidasNormalizadas.value.length}`,
      ];
      if (totalEstimado.value !== null) {
        infoLines.push(`Costo total estimado: ${formatMoneda(totalEstimado.value)}`);
      }

      infoLines.forEach((line) => {
        const wrapped = doc.splitTextToSize(line, CONTENT_W);
        doc.text(wrapped, M, y);
        y += 12;
      });

      y += 6;

      // Tabla de detalle
      const head = [
        [
          'Fecha',
          'ID Salida',
          'ID Unitaria',
          'Producto',
          'Cant.',
          'Costo unit.',
          'Siembra',
          'Registró',
          'Solicitó',
        ],
      ];

      const body = salidasNormalizadas.value.map((r) => [
        formatFecha(r.fecha),
        r.idSalida ?? '',
        r.idSalidaUnitaria ?? '',
        r.productoNombre ?? '',
        `${r.cantidad}${r.unidad ? ' ' + r.unidad : ''}`,
        r.costoUnitario != null ? formatMoneda(r.costoUnitario) : '',
        r.siembraId ? `#${r.siembraId} ${r.siembraNombre || ''}` : '',
        r.usuarioRegistro || '',
        r.solicitante || '',
      ]);

      autoTable(doc, {
        startY: y,
        head,
        body,
        margin: { left: M, right: M },
        styles: { font: 'helvetica', fontSize: 8, cellPadding: 4, overflow: 'linebreak' },
        headStyles: { fillColor: [37, 99, 235], textColor: 255, halign: 'center' },
        bodyStyles: { valign: 'top' },
        columnStyles: {
          0: { cellWidth: 60 },
          1: { cellWidth: 50 },
          2: { cellWidth: 55 },
          3: { cellWidth: 120 },
          4: { cellWidth: 45 },
          5: { cellWidth: 65 },
          6: { cellWidth: 85 },
          7: { cellWidth: 80 },
          8: { cellWidth: 80 },
        },
        didDrawPage: (data) => {
          // Pie con número de página
          const pageNumber = doc.internal.getNumberOfPages();
          setFont(9);
          doc.setTextColor(120);
          doc.text(
            `Página ${pageNumber}`,
            PAGE_W / 2,
            PAGE_H - 10,
            { align: 'center' }
          );
          doc.setTextColor(0);
        },
      });

      return doc;
    };

    const mostrarVistaPrevia = () => {
      if (!salidasNormalizadas.value.length) return;
      const doc = construirPDF();
      const blob = doc.output('blob');
      if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
      const url = URL.createObjectURL(blob);
      previewUrl.value = url;
      showPreview.value = true;
    };

    const cerrarPreview = () => {
      showPreview.value = false;
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value);
        previewUrl.value = null;
      }
    };

    const exportarPDF = () => {
      if (!salidasNormalizadas.value.length) return;
      const doc = construirPDF();
      doc.save(`reporte_salidas_${fechaInicio.value}_a_${fechaFin.value}.pdf`);
    };

    onMounted(() => {
      // Cargar reporte del mes actual por defecto
      cargarReporte();
    });

    return {
      fechaInicio,
      fechaFin,
      loading,
      errorMsg,
      rawSalidas,
      salidasNormalizadas,
      totalEstimado,
      rangoTexto,
      userName,
      farmName: acuicolaName,
      currentUserId,

      formatFecha,
      formatMoneda,
      cargarReporte,

      // PDF / preview
      showPreview,
      previewUrl,
      mostrarVistaPrevia,
      cerrarPreview,
      exportarPDF,
    };
  },
};
</script>

<style scoped>
.reporte-salidas {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px 10px 40px;
}

.card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
  padding: 20px 20px 24px;
}

.card--mt {
  margin-top: 24px;
}

.card__header {
  margin-bottom: 18px;
}

.card__header--compact {
  margin-bottom: 12px;
}

.card__title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #111827;
}

.card__sub {
  margin-top: 4px;
  font-size: 0.9rem;
  color: #6b7280;
}

.form-filtros {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  align-items: flex-end;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field--actions {
  align-items: flex-end;
}

.label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
}

.input {
  border-radius: 8px;
  border: 1px solid #d1d5db;
  padding: 8px 10px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.25);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 16px;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.btn--primary {
  background: #2563eb;
  color: #ffffff;
  box-shadow: 0 10px 18px rgba(37, 99, 235, 0.25);
}

.btn--primary:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.btn--outline {
  background: #ffffff;
  color: #2563eb;
  border: 1px solid #2563eb;
}

.btn--sm {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
}

.btn-row {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 16px;
}

.resumen {
  margin-top: 16px;
  font-size: 0.88rem;
  color: #374151;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 4px;
}

.error-msg {
  margin-top: 10px;
  color: #b91c1c;
  font-size: 0.85rem;
}

/* Tabla */
.table-wrap {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.table th,
.table td {
  padding: 8px 10px;
  border-bottom: 1px solid #e5e7eb;
}

.table th {
  text-align: left;
  font-weight: 600;
  color: #4b5563;
  background: #f9fafb;
}

.table tr:nth-child(even) td {
  background: #f9fafb;
}

.text-muted {
  color: #9ca3af;
}

.text-right {
  text-align: right;
}

.empty-state {
  padding: 12px 4px 8px;
  font-size: 0.9rem;
  color: #6b7280;
}

/* Modal preview */
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
}

.pdf-frame {
  width: 100%;
  height: 100%;
  border: 0;
}
</style>
