<template>
  <section class="proj container">
    <h2 class="proj__title">Proyección semanal</h2>
    <p class="text-muted">Edita fechas, supervivencia, talla y % de alimento; todo se recalcula al vuelo.</p>

    <!-- Controles -->
    <div class="card proj__controls">
      <div class="proj__grid">
        <div class="field">
          <label>Fecha inicial</label>
          <input class="input" type="date" v-model="state.fecha_inicio" />
        </div>
        <div class="field">
          <label>Semanas</label>
          <input class="input" type="number" min="1" max="60" v-model.number="state.semanas" @change="resizeRows" />
        </div>
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
          <label>Peso promedio inicial (g)</label>
          <input class="input" type="number" min="0" step="0.01" v-model.number="state.peso_inicial_g" />
          <small class="text-muted">Se usa como “semana 0” para el FCA de la semana 1.</small>
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
              <th style="min-width:120px">Fecha</th>
              <th style="min-width:145px">% Alimento por biomasa</th>
              <th style="min-width:140px">% Superv (acum)</th>
              <th style="min-width:120px">Talla (g)</th>
              <th style="min-width:110px">Org vivos</th>
              <th style="min-width:100px">Org/m²</th>
              <th style="min-width:125px">Crec. semanal (g)</th>
              <th style="min-width:115px">Biomasa (g)</th>
              <th style="min-width:135px">Alimento semanal (g)</th>
              <th style="min-width:120px">FCA semanal</th>
              <th style="min-width:90px">g/m³</th>
              <th class="col-shadow"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in rows" :key="i">
              <td class="cell-sticky left">{{ i + 1 }}</td>
              <td>{{ semanaFecha(i) }}</td>

              <!-- % alimento (manual) -->
              <td>
                <div class="cell-edit">
                  <input class="input input-cell" type="number" min="0" step="0.01" v-model.number="row.feed_pct" />
                  <span class="unit">%</span>
                </div>
              </td>

              <!-- Supervivencia (no creciente) -->
              <td>
                <div class="cell-edit">
                  <input
                    class="input input-cell"
                    type="number"
                    min="0"
                    max="100"
                    :value="row.superv_acum_pct"
                    @input="onSurvInput(i, $event.target.value)"
                    @blur="onSurvBlur(i)"
                  />
                  <span class="unit">%</span>
                </div>
              </td>

              <!-- Talla -->
              <td>
                <div class="cell-edit">
                  <input
                    class="input input-cell"
                    type="number"
                    min="0"
                    step="0.01"
                    :value="row.talla_g"
                    @input="onTallaInput(i, $event.target.value)"
                    @blur="onTallaBlur(i)"
                  />
                  <span class="unit">g</span>
                </div>
              </td>

              <td class="text-right">{{ fmt0(orgVivos(i)) }}</td>
              <td class="text-right">{{ fmt2(orgPorM2(i)) }}</td>
              <td class="text-right">{{ fmt2(crecSemanal(i)) }}</td>
              <td class="text-right">{{ fmt2(biomasaG(i)) }}</td>
              <td class="text-right">{{ fmt2(alimentoSemanalG(i)) }}</td>
              <td class="text-right">{{ fmt4(fcaSemanal(i)) }}</td>
              <td class="text-right">{{ fmt2(gramsPorM3(i)) }}</td>

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
          <strong>Sem {{ i + 1 }}</strong>
          <small class="text-muted">{{ semanaFecha(i) }}</small>
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
              <input
                class="input"
                type="number"
                min="0"
                max="100"
                :value="row.superv_acum_pct"
                @input="onSurvInput(i, $event.target.value)"
                @blur="onSurvBlur(i)"
              />
              <span class="unit">%</span>
            </div>
          </div>

          <div class="field">
            <label>Talla (g)</label>
            <div class="cell-edit">
              <input
                class="input"
                type="number"
                min="0"
                step="0.01"
                :value="row.talla_g"
                @input="onTallaInput(i, $event.target.value)"
                @blur="onTallaBlur(i)"
              />
              <span class="unit">g</span>
            </div>
          </div>

          <div class="stat"><span>Org vivos</span><strong>{{ fmt0(orgVivos(i)) }}</strong></div>
          <div class="stat"><span>Org/m²</span><strong>{{ fmt2(orgPorM2(i)) }}</strong></div>
          <div class="stat"><span>Crec. semanal</span><strong>{{ fmt2(crecSemanal(i)) }} g</strong></div>
          <div class="stat"><span>Biomasa</span><strong>{{ fmt2(biomasaG(i)) }} g</strong></div>
          <div class="stat"><span>Alim. semanal</span><strong>{{ fmt2(alimentoSemanalG(i)) }} g</strong></div>
          <div class="stat"><span>FCA semanal</span><strong>{{ fmt4(fcaSemanal(i)) }}</strong></div>
          <div class="stat"><span>g/m³</span><strong>{{ fmt2(gramsPorM3(i)) }}</strong></div>
        </div>
      </article>
    </div>

    <!-- Resumen -->
    <div class="proj__summary">
      <div class="row-card">
        <div class="stat"><span>Alimento total</span><strong>{{ fmt2(alimentoTotalKg) }} kg</strong></div>
        <div class="stat mt-1"><span>Biomasa final</span><strong>{{ fmt2(biomasaFinalKg) }} kg</strong></div>
        <div class="stat mt-1"><span>FCA global</span><strong>{{ fmt4(fcaGlobal) }}</strong></div>
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
    semanasDefault: { type: Number, default: 52 },
    fechaDefault: { type: String, default: () => new Date().toISOString().slice(0,10) },
    pesoInicialDefault: { type: Number, default: 2.35 },
  },
  setup(props) {
    const state = reactive({
      fecha_inicio: props.fechaDefault,
      semanas: props.semanasDefault,
      org_iniciales: props.siembra.organismos,
      area_m2: props.siembra.area_m2,
      volumen_m3: props.siembra.volumen_m3,
      peso_inicial_g: props.pesoInicialDefault,
    });

    const rows = ref([]);
    const makeRow = () => ({
      feed_pct: 0,
      superv_acum_pct: 100,
      talla_g: state.peso_inicial_g,
      touchedSurv: false,
      touchedTalla: false,
    });

    // ==== helpers supervivencia (definidos ANTES de usarlos) ====
    const prevSurv  = (i) => (i === 0 ? 100 : effectiveSurv(i - 1));
    const effectiveSurv = (i) => Math.min(rows.value[i].superv_acum_pct, prevSurv(i));

    function clampSurvivalChain(startIdx) {
      for (let j = startIdx; j < rows.value.length; j++) {
        const allowed = prevSurv(j);
        if (rows.value[j].superv_acum_pct > allowed) {
          rows.value[j].superv_acum_pct = allowed;
        }
      }
    }

    const onSurvInput = (i, val) => {
      const num = Math.max(0, Math.min(100, Number(val) || 0));
      rows.value[i].superv_acum_pct = Math.min(num, prevSurv(i));
      rows.value[i].touchedSurv = true;
      clampSurvivalChain(i + 1);
    };
    const onSurvBlur = (i) => {
      if (rows.value[i + 1] && !rows.value[i + 1].touchedSurv) {
        rows.value[i + 1].superv_acum_pct = rows.value[i].superv_acum_pct;
      }
    };

    // ==== talla ====
    const onTallaInput = (i, val) => {
      const num = Math.max(0, Number(val) || 0);
      rows.value[i].talla_g = num;
      rows.value[i].touchedTalla = true;
      if (rows.value[i + 1] && !rows.value[i + 1].touchedTalla) {
        rows.value[i + 1].talla_g = rows.value[i].talla_g;
      }
    };
    const onTallaBlur = () => {};

    // ==== filas ====
    const resizeRows = () => {
      const n = Math.max(1, Math.min(60, Number(state.semanas) || 1));
      while (rows.value.length < n) rows.value.push(makeRow());
      while (rows.value.length > n) rows.value.pop();
      // carry de valores por defecto
      for (let i = 1; i < rows.value.length; i++) {
        if (!rows.value[i].touchedTalla) rows.value[i].talla_g = rows.value[i - 1].talla_g;
        if (!rows.value[i].touchedSurv)
          rows.value[i].superv_acum_pct = Math.min(rows.value[i - 1].superv_acum_pct, rows.value[i].superv_acum_pct);
      }
      clampSurvivalChain(0);
    };
    // Inicializa ahora que ya existen todas las funciones usadas:
    resizeRows();

    // ==== fechas ====
    const semanaFecha = (i) => {
      if (!state.fecha_inicio) return "";
      const d = new Date(state.fecha_inicio);
      if (isNaN(d)) return "";
      const nd = new Date(d.getTime() + i * 7 * 24 * 60 * 60 * 1000);
      return nd.toISOString().slice(0, 10);
    };

    // ==== cálculos ====
    const orgVivos = (i) => Math.max(0, Math.round(state.org_iniciales * (effectiveSurv(i) / 100)));
    const orgPorM2 = (i) => (state.area_m2 ? orgVivos(i) / state.area_m2 : 0);
    const tallaPrev = (i) => (i === 0 ? state.peso_inicial_g : rows.value[i - 1].talla_g);
    const survPrev  = (i) => (i === 0 ? 100 : effectiveSurv(i - 1));

    const biomasaG = (i) => orgVivos(i) * rows.value[i].talla_g;
    const biomasaPrevG = (i) => {
      const orgPrev = Math.max(0, Math.round(state.org_iniciales * (survPrev(i) / 100)));
      return orgPrev * tallaPrev(i);
    };

    const crecSemanal = (i) => rows.value[i].talla_g - tallaPrev(i);
    const alimentoSemanalG = (i) => biomasaG(i) * (rows.value[i].feed_pct / 100) * 7;
    const fcaSemanal = (i) => {
      const gain = Math.max(1e-6, biomasaG(i) - biomasaPrevG(i));
      return alimentoSemanalG(i) / gain;
    };
    const gramsPorM3 = (i) => (state.volumen_m3 ? biomasaG(i) / state.volumen_m3 : 0);

    const alimentoTotalKg = computed(() => rows.value.reduce((acc, _r, i) => acc + alimentoSemanalG(i), 0) / 1000);
    const biomasaFinalKg = computed(() => biomasaG(rows.value.length - 1) / 1000);
    const fcaGlobal = computed(() => {
      const bio0 = biomasaPrevG(0);
      const bioF = biomasaG(rows.value.length - 1);
      const gain = Math.max(1e-6, bioF - bio0);
      return (alimentoTotalKg.value * 1000) / gain;
    });

    // ==== responsive ====
    const isMobile = ref(false);
    const mq = window.matchMedia("(max-width: 768px)");
    const updateMobile = () => (isMobile.value = mq.matches);
    onMounted(() => {
      updateMobile();
      mq.addEventListener?.("change", updateMobile);
    });
    onBeforeUnmount(() => mq.removeEventListener?.("change", updateMobile));

    // formatos
    const fmt0 = (v) => (isFinite(v) ? Number(v).toFixed(0) : "0");
    const fmt2 = (v) => (isFinite(v) ? Number(v).toFixed(2) : "0.00");
    const fmt4 = (v) => (isFinite(v) ? Number(v).toFixed(4) : "0.0000");

    return {
      state, rows,
      // inputs
      onSurvInput, onSurvBlur, onTallaInput, onTallaBlur,
      // fechas
      semanaFecha,
      // cálculos
      orgVivos, orgPorM2, crecSemanal, biomasaG, alimentoSemanalG, fcaSemanal, gramsPorM3,
      alimentoTotalKg, biomasaFinalKg, fcaGlobal,
      // ui
      resizeRows, isMobile,
      // fmt
      fmt0, fmt2, fmt4,
    };
  },
};
</script>

<style scoped>
.proj { padding-block: 8px; }
.proj__title { margin: 0 0 6px; }
.proj__controls { margin: 10px 0 14px; }
.proj__grid { display: grid; gap: 12px; grid-template-columns: repeat(6, minmax(160px, 1fr)); }
@media (max-width: 1200px){ .proj__grid{ grid-template-columns: repeat(3,1fr);} }
@media (max-width: 768px){ .proj__grid{ grid-template-columns: 1fr;} }

/* Tabla */
.table-holder{ overflow: hidden; }
.table-wrap{ overflow:auto; border:1px solid var(--color-border,#e5e7eb); border-radius: var(--radius-lg,14px); }
.table{ width:100%; border-collapse:separate; border-spacing:0; font-size:14px; background:var(--color-surface,#fff); }
.table th,.table td{ padding:10px 12px; border-bottom:1px solid var(--color-border,#e5e7eb); }
.table th{
  position:sticky; top:0; z-index:3; background:#f8f9fa; color:#374151; font-weight:600;
  box-shadow:0 1px 0 var(--color-border,#e5e7eb);
}
.table thead th:first-child{ border-top-left-radius:12px; }
.table thead th:last-child{ border-top-right-radius:12px; }
.table tbody tr:hover td{ background:#f3fdf6; }
.table tbody tr:nth-child(even) td{ background:rgba(0,0,0,.02); }

/* Sticky izquierda */
.cell-sticky.left{ position:sticky; left:0; z-index:4; background:#f8f9fa; box-shadow:1px 0 0 var(--color-border,#e5e7eb); }

/* Sombra derecha fija */
.col-shadow{ position:sticky; right:0; width:14px; min-width:14px; padding:0; z-index:4;
  background:linear-gradient(to left, rgba(0,0,0,.12), rgba(0,0,0,0)); border-bottom:none;}
.table thead .col-shadow{ border-top-right-radius:12px; }

/* Edición */
.cell-edit{ display:flex; align-items:center; gap:6px; }
.input-cell{ width:7.5rem; text-align:right; }
.unit{ font-size:12px; color:var(--color-muted,#6b7280); }

/* Tarjetas móvil */
.proj-cards{ display:grid; gap:12px; }
.proj-card__head{ display:flex; justify-content:space-between; margin-bottom:8px; }
.proj-card__grid{ display:grid; gap:10px; grid-template-columns: 1fr 1fr; }
@media (max-width:480px){ .proj-card__grid{ grid-template-columns:1fr; } }

/* Theme */
.card{
  background:var(--color-surface,#fff); color:var(--color-text,#1f2937);
  border:1px solid var(--color-border,#e5e7eb); border-radius:var(--radius-lg,14px);
  box-shadow:var(--shadow-md,0 4px 12px rgba(0,0,0,.10)); padding:16px;
}
.row-card{ border-radius:var(--radius-lg,14px); border:1px solid var(--color-border,#e5e7eb);
  background:var(--color-surface,#fff); padding:14px; box-shadow:var(--shadow-sm,0 2px 8px rgba(0,0,0,.06)); }
.stat{ display:flex; align-items:center; justify-content:space-between; background:#f8fafc; border:1px solid #eef2f7; border-radius:var(--radius-md,10px); padding:8px 10px; }
.stat span{ color:var(--color-muted,#6b7280); }
.stat strong{ color:var(--color-text,#1f2937); }

.text-right{ text-align:right; }
.mt-1{ margin-top:.25rem; }
</style>
