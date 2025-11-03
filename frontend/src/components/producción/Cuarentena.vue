<template>
  <section class="proj container">
    <h2 class="proj__title">Proyección semanal</h2>
    <p class="text-muted">Edita los porcentajes y tallas; todo se recalcula al vuelo.</p>

    <!-- Controles -->
    <div class="card proj__controls">
      <div class="proj__grid">
        <div class="field">
          <label>Organismos iniciales</label>
          <input class="input" type="number" min="1" v-model.number="state.org_iniciales" />
        </div>
        <div class="field">
          <label>Área (m²)</label>
          <input class="input" type="number" min="0.01" step="0.01" v-model.number="state.area_m2" />
        </div>
        <div class="field">
          <label>Volumen (m³)</label>
          <input class="input" type="number" min="0.01" step="0.01" v-model.number="state.volumen_m3" />
        </div>
        <div class="field">
          <label>Semanas</label>
          <input class="input" type="number" min="1" max="60" v-model.number="state.semanas" @change="resizeRows" />
        </div>
        <div class="field">
          <label>% Alimento por biomasa (por semana)</label>
          <small class="text-muted">Puedes ajustar por fila abajo.</small>
        </div>
      </div>
    </div>

    <!-- ====== Tabla (desktop / tablet) ====== -->
    <div class="card table-holder" v-if="!isMobile">
      <div class="table-wrap">
        <table class="table table--zebra">
          <thead>
            <tr>
              <th class="cell-sticky left">Sem</th>
              <th style="min-width:145px">% Alimento por biomasa</th>
              <th style="min-width:140px">% Superv (acum)</th>
              <th style="min-width:120px">Talla (g)</th>
              <th style="min-width:110px">Org vivos</th>
              <th style="min-width:100px">Org/m²</th>
              <th style="min-width:125px">Crec. semanal (g)</th>
              <th style="min-width:115px">Crec. diario (g)</th>
              <th style="min-width:115px">Biomasa (g)</th>
              <th style="min-width:125px">Alimento diario (g)</th>
              <th style="min-width:135px">Alimento semanal (g)</th>
              <th style="min-width:155px">Alimento acumulado (g)</th>
              <th style="min-width:90px">FCA</th>
              <th style="min-width:90px">g/m³</th>

              <!-- Columna sombra sticky a la derecha -->
              <th class="col-shadow"></th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(row, i) in rows" :key="i">
              <!-- Semana (única sticky a la izquierda) -->
              <td class="cell-sticky left">{{ i + 1 }}</td>

              <!-- % alimento por biomasa (editable por fila) -->
              <td>
                <div class="cell-edit">
                  <input class="input input-cell" type="number" min="0" step="0.01"
                         v-model.number="row.feed_pct" />
                  <span class="unit">%</span>
                </div>
              </td>

              <!-- % Supervivencia (acumulado) -->
              <td>
                <div class="cell-edit">
                  <input class="input input-cell" type="number" min="0" max="100"
                         v-model.number="row.superv_acum_pct" />
                  <span class="unit">%</span>
                </div>
              </td>

              <!-- Talla (g) -->
              <td>
                <div class="cell-edit">
                  <input class="input input-cell" type="number" min="0" step="0.01"
                         v-model.number="row.talla_g" />
                  <span class="unit">g</span>
                </div>
              </td>

              <td class="text-right">{{ fmt0(calc.orgVivos(i)) }}</td>
              <td class="text-right">{{ fmt2(calc.orgPorM2(i)) }}</td>
              <td class="text-right">{{ fmt2(calc.crecSemanal(i)) }}</td>
              <td class="text-right">{{ fmt4(calc.crecDiario(i)) }}</td>
              <td class="text-right">{{ fmt2(calc.biomasaG(i)) }}</td>
              <td class="text-right">{{ fmt2(calc.alimentoDiarioG(i)) }}</td>
              <td class="text-right">{{ fmt2(calc.alimentoSemanalG(i)) }}</td>
              <td class="text-right">{{ fmt2(calc.alimentoAcumuladoG(i)) }}</td>
              <td class="text-right">{{ fmt4(calc.fca(i)) }}</td>
              <td class="text-right">{{ fmt2(calc.gramsPorM3(i)) }}</td>

              <!-- Celda “sombra” pegada al borde derecho (vacía) -->
              <td class="col-shadow"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ====== Tarjetas (móvil) ====== -->
    <div class="proj-cards" v-else>
      <article v-for="(row,i) in rows" :key="'card-'+i" class="card proj-card">
        <header class="proj-card__head">
          <strong>Semana {{ i + 1 }}</strong>
        </header>

        <div class="proj-card__grid">
          <div class="field">
            <label>% Alimento por biomasa</label>
            <div class="cell-edit">
              <input class="input" type="number" min="0" step="0.01" v-model.number="row.feed_pct" />
              <span class="unit">%</span>
            </div>
          </div>

          <div class="field">
            <label>% Superv (acum)</label>
            <div class="cell-edit">
              <input class="input" type="number" min="0" max="100" v-model.number="row.superv_acum_pct" />
              <span class="unit">%</span>
            </div>
          </div>

          <div class="field">
            <label>Talla (g)</label>
            <div class="cell-edit">
              <input class="input" type="number" min="0" step="0.01" v-model.number="row.talla_g" />
              <span class="unit">g</span>
            </div>
          </div>

          <div class="stat"><span>Org vivos</span><strong>{{ fmt0(calc.orgVivos(i)) }}</strong></div>
          <div class="stat"><span>Org/m²</span><strong>{{ fmt2(calc.orgPorM2(i)) }}</strong></div>
          <div class="stat"><span>Crec. semanal</span><strong>{{ fmt2(calc.crecSemanal(i)) }} g</strong></div>
          <div class="stat"><span>Crec. diario</span><strong>{{ fmt4(calc.crecDiario(i)) }} g</strong></div>
          <div class="stat"><span>Biomasa</span><strong>{{ fmt2(calc.biomasaG(i)) }} g</strong></div>
          <div class="stat"><span>Alim. diario</span><strong>{{ fmt2(calc.alimentoDiarioG(i)) }} g</strong></div>
          <div class="stat"><span>Alim. semanal</span><strong>{{ fmt2(calc.alimentoSemanalG(i)) }} g</strong></div>
          <div class="stat"><span>Alim. acumulado</span><strong>{{ fmt2(calc.alimentoAcumuladoG(i)) }} g</strong></div>
          <div class="stat"><span>FCA</span><strong>{{ fmt4(calc.fca(i)) }}</strong></div>
          <div class="stat"><span>g/m³</span><strong>{{ fmt2(calc.gramsPorM3(i)) }}</strong></div>
        </div>
      </article>
    </div>

    <!-- Resumen -->
    <div class="proj__summary">
      <div class="row-card">
        <div class="stat"><span>Alimento total</span><strong>{{ fmt2(alimentoTotalKg) }} kg</strong></div>
        <div class="stat mt-1"><span>Biomasa final</span><strong>{{ fmt2(biomasaFinalKg) }} kg</strong></div>
        <div class="stat mt-1"><span>FCA final</span><strong>{{ fmt4(fcaFinal) }}</strong></div>
      </div>
    </div>
  </section>
</template>

<script>
import { reactive, ref, computed, onMounted, onBeforeUnmount } from "vue";

export default {
  name: "ProyeccionSemanal",
  props: {
    siembra: {
      type: Object,
      default: () => ({ organismos: 5000, area_m2: 125, volumen_m3: 125 }),
    },
    semanasDefault: { type: Number, default: 12 },
  },
  setup(props) {
    const state = reactive({
      org_iniciales: props.siembra.organismos,
      area_m2: props.siembra.area_m2,
      volumen_m3: props.siembra.volumen_m3,
      semanas: props.semanasDefault,
    });

    const rows = ref([]);
    const makeRow = () => ({
      feed_pct: 0,          // % alimento por biomasa (fila)
      superv_acum_pct: 100, // % acumulado vivo
      talla_g: 2.35,
    });

    const resizeRows = () => {
      const n = Math.max(1, Math.min(60, Number(state.semanas) || 1));
      while (rows.value.length < n) rows.value.push(makeRow());
      while (rows.value.length > n) rows.value.pop();
    };
    resizeRows();

    const calc = {
      orgVivos(i) { return Math.max(0, Math.round(state.org_iniciales * (rows.value[i].superv_acum_pct / 100))); },
      orgPorM2(i) { const v = this.orgVivos(i); return state.area_m2 ? v / state.area_m2 : 0; },
      crecSemanal(i) { const prev = i > 0 ? rows.value[i - 1].talla_g : rows.value[i].talla_g; return rows.value[i].talla_g - prev; },
      crecDiario(i) { return this.crecSemanal(i) / 7; },
      biomasaG(i) { return this.orgVivos(i) * rows.value[i].talla_g; },
      alimentoDiarioG(i) { return this.biomasaG(i) * (rows.value[i].feed_pct / 100); },
      alimentoSemanalG(i) { return this.alimentoDiarioG(i) * 7; },
      alimentoAcumuladoG(i) { let acc = 0; for (let k = 0; k <= i; k++) acc += this.alimentoSemanalG(k); return acc; },
      gramsPorM3(i) { return state.volumen_m3 ? this.biomasaG(i) / state.volumen_m3 : 0; },
      fca(i) {
        const bio0 = this.biomasaG(0);
        const bioi = this.biomasaG(i);
        const gain = Math.max(1e-6, bioi - bio0);
        return this.alimentoAcumuladoG(i) / gain;
      },
    };

    const biomasaFinalKg = computed(() => calc.biomasaG(rows.value.length - 1) / 1000);
    const alimentoTotalKg = computed(() => calc.alimentoAcumuladoG(rows.value.length - 1) / 1000);
    const fcaFinal = computed(() => calc.fca(rows.value.length - 1));

    // ====== Responsive (tabla ↔ tarjetas)
    const isMobile = ref(false);
    const mq = window.matchMedia("(max-width: 768px)");
    const updateMobile = () => (isMobile.value = mq.matches);
    onMounted(() => { updateMobile(); mq.addEventListener?.("change", updateMobile); });
    onBeforeUnmount(() => { mq.removeEventListener?.("change", updateMobile); });

    // helpers de formato
    const fmt0 = (v) => (isFinite(v) ? Number(v).toFixed(0) : "0");
    const fmt2 = (v) => (isFinite(v) ? Number(v).toFixed(2) : "0.00");
    const fmt4 = (v) => (isFinite(v) ? Number(v).toFixed(4) : "0.0000");

    return {
      state, rows, resizeRows, calc,
      alimentoTotalKg, biomasaFinalKg, fcaFinal,
      fmt0, fmt2, fmt4,
      isMobile,
    };
  },
};
</script>

<style scoped>
/* ===== Encabezado y controles ===== */
.proj { padding-block: 8px; }
.proj__title { margin: 0 0 6px; }
.proj__controls { margin: 10px 0 14px; }
.proj__grid { display: grid; gap: 12px; grid-template-columns: repeat(5, minmax(160px, 1fr)); }
@media (max-width: 1100px) { .proj__grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px)  { .proj__grid { grid-template-columns: 1fr; } }

/* ===== Tabla ===== */
.table-holder { overflow: hidden; } /* mantiene los radios del card */
.table-wrap { overflow: auto; border: 1px solid var(--color-border,#e5e7eb); border-radius: var(--radius-lg,14px); }
.table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 14px; background: var(--color-surface,#fff); }
.table th, .table td { padding: 10px 12px; border-bottom: 1px solid var(--color-border,#e5e7eb); }
.table th {
  position: sticky; top: 0; z-index: 3;
  background: #f8f9fa; color: #374151; font-weight: 600;
  box-shadow: 0 1px 0 var(--color-border,#e5e7eb);
}
/* bordes superiores redondeados del header */
.table thead th:first-child { border-top-left-radius: 12px; }
.table thead th:last-child  { border-top-right-radius: 12px; }

/* Zebra + hover */
.table tbody tr:hover td { background: #f3fdf6; }
.table tbody tr:nth-child(even) td { background: rgba(0,0,0,.02); }

/* Sticky izquierda: SOLO la columna "Sem" */
.cell-sticky.left { position: sticky; left: 0; z-index: 4; background: #f8f9fa; box-shadow: 1px 0 0 var(--color-border,#e5e7eb); }

/* Columna sombra a la derecha (overlay fijo) */
.col-shadow { position: sticky; right: 0; width: 14px; min-width: 14px; padding: 0; z-index: 4; background: linear-gradient(to left, rgba(0,0,0,.12), rgba(0,0,0,0)); border-bottom: none; }
.table thead .col-shadow { border-top-right-radius: 12px; }

/* Celdas de edición */
.cell-edit { position: relative; display: flex; align-items: center; gap: 6px; }
.input-cell { width: 7.5rem; text-align: right; }
.unit { font-size: 12px; color: var(--color-muted,#6b7280); }

/* ===== Tarjetas (móvil) ===== */
.proj-cards { display: grid; gap: 12px; }
.proj-card__head { margin-bottom: 8px; }
.proj-card__grid { display: grid; gap: 10px; grid-template-columns: 1fr 1fr; }
@media (max-width: 480px) { .proj-card__grid { grid-template-columns: 1fr; } }

/* Tarjetas / utilitarios (alineados a tu theme) */
.card {
  background: var(--color-surface,#fff);
  color: var(--color-text,#1f2937);
  border: 1px solid var(--color-border,#e5e7eb);
  border-radius: var(--radius-lg,14px);
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,.10));
  padding: 16px;
}
.row-card { border-radius: var(--radius-lg,14px); border: 1px solid var(--color-border,#e5e7eb); background: var(--color-surface,#fff); padding: 14px; box-shadow: var(--shadow-sm,0 2px 8px rgba(0,0,0,.06)); }
.stat { display: flex; align-items: center; justify-content: space-between; background: #f8fafc; border: 1px solid #eef2f7; border-radius: var(--radius-md,10px); padding: 8px 10px; }
.stat span { color: var(--color-muted,#6b7280); }
.stat strong { color: var(--color-text,#1f2937); }

.text-right { text-align: right; }
.mt-1 { margin-top: .25rem; }
</style>
