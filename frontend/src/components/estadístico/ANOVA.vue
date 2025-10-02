<template>
  <div class="grafico-container">
    <h1>ANOVA de un Factor</h1>

    <form class="form-seleccion one-col" @submit.prevent="ejecutarANOVA">
      <!-- Barra superior -->
      <div class="toolbar-top">
        <div class="row">
          <div class="col">
            <label>Fuente de datos</label>
            <select v-model="fuente" required>
              <option value="crecimiento">Crecimiento</option>
              <option value="calidad">Calidad de Agua</option>
            </select>
          </div>
          <div class="col">
            <label>Variable</label>
            <select v-model="variableSeleccionada" required>
              <option disabled value="">Seleccione…</option>
              <option v-for="opt in variablesDisponibles" :key="opt.key" :value="opt.key">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div class="col">
            <label>Periodo</label>
            <select v-model="periodoSemanas" required>
              <option value="all">Completo</option>
              <option v-for="n in [4,8,12,16,24,52]" :key="n" :value="n">Últimas {{ n }} semanas</option>
            </select>
          </div>
          <div class="col">
            <label>α (significancia)</label>
            <input type="number" v-model.number="alpha" min="0.0001" max="0.5" step="0.0001">
          </div>
        </div>
      </div>

      <!-- Estanques y siembras -->
      <div class="card">
        <label class="block-title">Estanques y Siembras</label>
        <input v-model="busquedaEstanque" type="text" class="input" placeholder="Buscar estanque…"/>

        <ul class="list ponds">
          <li v-for="e in estanquesFiltrados" :key="e.id_estanque" class="pond-row">
            <div class="pond-row-main clickable" @click="toggleExpand(e.id_estanque)">
              <span class="pond-name">{{ e.nombre }}</span>
              <div class="pond-meta">
                <small class="meta">{{ conteoSiembras(e.id_estanque) }} siembras</small>
                <span class="chev">{{ expandido[e.id_estanque] ? '▲' : '▼' }}</span>
              </div>
            </div>

            <transition name="fade">
              <div v-if="expandido[e.id_estanque]" class="siembras-panel" @click.stop>
                <div class="panel-actions">
                  <button type="button" class="btn-sm" @click="seleccionarTodasDeEstanque(e.id_estanque)">Seleccionar todas</button>
                  <button type="button" class="btn-sm outline" @click="limpiarDeEstanque(e.id_estanque)">Limpiar</button>
                </div>

                <input
                  v-model="busquedaSiembra[e.id_estanque]"
                  type="text"
                  class="input small"
                  :placeholder="`Buscar siembras de ${e.nombre}…`"
                />

                <ul class="siembras-list">
                  <li v-for="s in siembrasDeEstanqueFiltradas(e.id_estanque)" :key="s.id_siembra">
                    <label class="checkbox-label">
                      <input type="checkbox" :value="s.id_siembra" v-model="siembrasSeleccionadas" />
                      <span>{{ etiquetaSiembra(s) }}</span>
                    </label>
                    <div class="grp-buttons">
                      <button
                        v-for="g in GRUPO_MAX"
                        :key="g"
                        type="button"
                        class="grp-btn"
                        :class="{active: grupoDeSiembra(s.id_siembra)===g}"
                        @click="toggleGrupo(s.id_siembra,g)"
                        :title="`Grupo ${g}`"
                      >{{ g }}</button>
                    </div>
                  </li>
                </ul>
              </div>
            </transition>
          </li>
        </ul>

        <div class="card inner">
          <label class="block-title">Selección</label>
          <div class="chips" v-if="siembrasSeleccionadas.length">
            <span class="chip" v-for="sid in siembrasSeleccionadas" :key="sid">
              {{ nickSiembra(sid) }}
              <button type="button" class="chip-x" @click="quitarSiembra(sid)">×</button>
            </span>
          </div>
          <div class="muted" v-else>Sin siembras seleccionadas.</div>

          <div class="quick-actions">
            <button type="button" class="btn-sm" @click="seleccionarTodasVisibles">Seleccionar visibles</button>
            <button type="button" class="btn-sm outline" @click="limpiarSeleccion">Limpiar</button>
          </div>

          <div class="grupos-summary">
            <div v-for="g in grupos" :key="g.gid" class="grupo-line" v-show="g.ids.length">
              <strong>Grupo {{ g.gid }}:</strong>
              <span class="chip tiny" v-for="sid in g.ids" :key="`G${g.gid}-${sid}`">
                {{ nickSiembra(sid) }}
                <button type="button" class="chip-x" @click="removerDeGrupo(sid)">×</button>
              </span>
              <button type="button" class="btn-sm outline" @click="vaciarGrupo(g.gid)">Vaciar {{ g.gid }}</button>
            </div>
          </div>
        </div>
      </div>

      <div class="btn-row">
        <button type="submit" class="btn-generar" :disabled="!puedeEjecutar">
          Ejecutar ANOVA
        </button>
      </div>
    </form>

    <!-- Resultados -->
    <div v-if="resumen && resultadosSemanales.length" class="resultados">
      <div class="chart-header">
        <h3>Media por grupo — {{ labelVariable }}</h3>
        <div class="row" style="gap:8px;">
          <label>Semana</label>
          <select v-model.number="semanaGrafico">
            <option v-for="w in semanasDisponibles" :key="w" :value="w">Semana {{ w }}</option>
          </select>
        </div>
      </div>
      <div class="chart-wrap">
        <canvas id="grafico-anova"></canvas>
      </div>

      <!-- === NUEVO: Tukey por semana (aprox Sidák) === -->
      <div class="card" v-if="tukeyByWeek[semanaGrafico]">
        <h3>Tukey-Kramer (aprox. Sidák) — Semana {{ semanaGrafico }} (α={{ alpha }})</h3>
        <div class="muted" style="margin:6px 0 10px;">
          Letras sobre el gráfico = grupos sin diferencias significativas comparten letra.
        </div>

        <table class="stats-table" style="margin-top:8px;">
          <thead>
            <tr>
              <th>Grupo</th><th>n</th><th>Media</th><th>DE</th><th>Letra</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="g in tukeyByWeek[semanaGrafico].order" :key="'tl-'+g">
              <td>{{ g }}</td>
              <td>{{ tukeyByWeek[semanaGrafico].stats[g].n }}</td>
              <td>{{ fmt(tukeyByWeek[semanaGrafico].stats[g].mean,3) }}</td>
              <td>{{ fmt(tukeyByWeek[semanaGrafico].stats[g].sd,3) }}</td>
              <td style="font-weight:700">{{ tukeyByWeek[semanaGrafico].letters[g] }}</td>
            </tr>
          </tbody>
        </table>

        <div class="card inner" v-if="tukeyByWeek[semanaGrafico].pairs.length">
          <div class="block-title">Comparaciones por pares</div>
          <table class="stats-table">
            <thead>
              <tr>
                <th>Par</th>
                <th>Δ medias</th>
                <th>q</th>
                <th>IC (95% aprox)</th>
                <th>p<sub>adj</sub> (aprox)</th>
                <th>Rechaza</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p,idx) in tukeyByWeek[semanaGrafico].pairs" :key="'pw-'+idx">
                <td>{{ p.g1 }} vs {{ p.g2 }}</td>
                <td>{{ fmt(p.meandiff,4) }}</td>
                <td>{{ fmt(p.q,4) }}</td>
                <td>[{{ fmt(p.lower,4) }}, {{ fmt(p.upper,4) }}]</td>
                <td>{{ p.p_adj!=null ? fmt(p.p_adj,4) : '—' }}</td>
                <td :style="{color: p.reject ? '#c0392b' : '#27ae60'}">{{ p.reject ? 'Sí' : 'No' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- === NUEVO: Tukey Global (aprox Sidák) === -->
      <div class="card" v-if="tukeyGlobal">
        <h3>Tukey-Kramer Global (aprox. Sidák) — α={{ alpha }}</h3>
        <table class="stats-table">
          <thead>
            <tr>
              <th>Grupo</th><th>n</th><th>Media</th><th>DE</th><th>Letra</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="g in tukeyGlobal.order" :key="'tgl-'+g">
              <td>{{ g }}</td>
              <td>{{ tukeyGlobal.stats[g].n }}</td>
              <td>{{ fmt(tukeyGlobal.stats[g].mean,3) }}</td>
              <td>{{ fmt(tukeyGlobal.stats[g].sd,3) }}</td>
              <td style="font-weight:700">{{ tukeyGlobal.letters[g] }}</td>
            </tr>
          </tbody>
        </table>

        <div class="card inner" v-if="tukeyGlobal.pairs.length">
          <div class="block-title">Comparaciones por pares (Global)</div>
          <table class="stats-table">
            <thead>
              <tr>
                <th>Par</th>
                <th>Δ medias</th>
                <th>q</th>
                <th>IC (95% aprox)</th>
                <th>p<sub>adj</sub> (aprox)</th>
                <th>Rechaza</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p,idx) in tukeyGlobal.pairs" :key="'pg-'+idx">
                <td>{{ p.g1 }} vs {{ p.g2 }}</td>
                <td>{{ fmt(p.meandiff,4) }}</td>
                <td>{{ fmt(p.q,4) }}</td>
                <td>[{{ fmt(p.lower,4) }}, {{ fmt(p.upper,4) }}]</td>
                <td>{{ p.p_adj!=null ? fmt(p.p_adj,4) : '—' }}</td>
                <td :style="{color: p.reject ? '#c0392b' : '#27ae60'}">{{ p.reject ? 'Sí' : 'No' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h3>ANOVA por semana (α={{ alpha }})</h3>
        <table class="stats-table">
          <thead>
            <tr>
              <th>Semana</th>
              <th>k</th>
              <th>N</th>
              <th>F</th>
              <th>p</th>
              <th>η²</th>
              <th>ω²</th>
              <th>Signif.</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in resultadosSemanales" :key="`w-${r.week}`">
              <td>Semana {{ r.week }}</td>
              <td>{{ r.k }}</td>
              <td>{{ r.n }}</td>
              <td>{{ fmt(r.F) }}</td>
              <td>{{ fmt(r.p) }}</td>
              <td>{{ fmt(r.eta2) }}</td>
              <td>{{ fmt(r.omega2) }}</td>
              <td :style="{color: r.p < alpha ? '#c0392b' : '#27ae60'}">
                {{ r.p < alpha ? 'Sí' : 'No' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <h3>ANOVA global (todas las semanas)</h3>
        <table class="stats-table">
          <thead>
            <tr>
              <th>k</th>
              <th>N</th>
              <th>F</th>
              <th>p</th>
              <th>η²</th>
              <th>ω²</th>
              <th>Signif.</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ resumen.global.k }}</td>
              <td>{{ resumen.global.n }}</td>
              <td>{{ fmt(resumen.global.F) }}</td>
              <td>{{ fmt(resumen.global.p) }}</td>
              <td>{{ fmt(resumen.global.eta2) }}</td>
              <td>{{ fmt(resumen.global.omega2) }}</td>
              <td :style="{color: resumen.global.p < alpha ? '#c0392b' : '#27ae60'}">
                {{ resumen.global.p < alpha ? 'Sí' : 'No' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Datos utilizados -->
      <div class="card">
        <div class="chart-header">
          <span class="block-title">Datos utilizados</span>
          <span class="muted">Valores crudos y estadísticos usados en el ANOVA</span>
        </div>

        <!-- Global -->
        <h4 style="margin:8px 0 6px">Global</h4>
        <table class="stats-table">
          <thead>
            <tr>
              <th>Grupo</th><th>n</th><th>Media</th><th>DE</th><th>Mín</th><th>Mediana</th><th>Máx</th><th>Valores (crudos)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="label in Object.keys(rawGlobalByGroup)" :key="'g-'+label">
              <td>{{ label }}</td>
              <td>{{ statsGlobalByGroup[label]?.n ?? 0 }}</td>
              <td>{{ (statsGlobalByGroup[label]?.mean ?? 0).toFixed(3) }}</td>
              <td>{{ (statsGlobalByGroup[label]?.sd ?? 0).toFixed(3) }}</td>
              <td>{{ statsGlobalByGroup[label]?.min ?? '—' }}</td>
              <td>{{ (statsGlobalByGroup[label]?.median ?? 0).toFixed(3) }}</td>
              <td>{{ statsGlobalByGroup[label]?.max ?? '—' }}</td>
              <td style="text-align:left">
                <details>
                  <summary>ver</summary>
                  <div style="font-family: ui-monospace,Consolas,monospace; white-space:normal; word-break:break-word;">
                    {{ rawGlobalByGroup[label]?.join(", ") || "—" }}
                  </div>
                </details>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Semanales -->
        <div v-for="wk in semanasDisponibles" :key="'w-'+wk" class="card inner">
          <div class="block-title">Semana {{ wk }}</div>
          <table class="stats-table">
            <thead>
              <tr>
                <th>Grupo</th><th>n</th><th>Media</th><th>DE</th><th>Mín</th><th>Mediana</th><th>Máx</th><th>Valores (crudos)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="label in Object.keys(rawGlobalByGroup)" :key="`w${wk}-${label}`">
                <td>{{ label }}</td>
                <td>{{ statsByWeekGroup[wk]?.[label]?.n ?? 0 }}</td>
                <td>{{ (statsByWeekGroup[wk]?.[label]?.mean ?? 0).toFixed(3) }}</td>
                <td>{{ (statsByWeekGroup[wk]?.[label]?.sd ?? 0).toFixed(3) }}</td>
                <td>{{ statsByWeekGroup[wk]?.[label]?.min ?? '—' }}</td>
                <td>{{ (statsByWeekGroup[wk]?.[label]?.median ?? 0).toFixed(3) }}</td>
                <td>{{ statsByWeekGroup[wk]?.[label]?.max ?? '—' }}</td>
                <td style="text-align:left">
                  <details>
                    <summary>ver</summary>
                    <div style="font-family: ui-monospace,Consolas,monospace; white-space:normal; word-break:break-word;">
                      {{ (rawByWeekGroup[wk] && rawByWeekGroup[wk][label]) ? rawByWeekGroup[wk][label].join(", ") : "—" }}
                    </div>
                  </details>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Botonera PDF/Excel -->
      <div class="btn-row">
        <button type="button" class="btn-generar outline" @click="mostrarVistaPrevia">Vista previa PDF</button>
        <button type="button" class="btn-generar" @click="exportarExcel">Exportar Excel</button>
        <button type="button" class="btn-generar" @click="exportarPDF">Descargar PDF</button>
      </div>
    </div>

    <!-- Modal PDF -->
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
import { ref, computed, onMounted, nextTick, watch } from "vue";
import axios from "@/services/axios";

import { Chart } from "chart.js/auto";
import "@sgratzl/chartjs-chart-boxplot";

import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import { jStat } from "jstat";

/** ================= Utils numéricos ================= **/
function fcdf(x, df1, df2) { if (x <= 0) return 0; return jStat.centralF.cdf(x, df1, df2); }

const MSW = 7*24*60*60*1000;
const formatDate = (d) => new Date(d).toISOString().split("T")[0];
const fmt = (v, d=4) => (v==null||Number.isNaN(v)) ? "—" : Number(v).toFixed(d);
const mean = (a) => a.length ? a.reduce((s,v)=>s+v,0)/a.length : 0;
const variance = (a, m=mean(a)) => a.length>1 ? a.reduce((s,v)=>s+(v-m)*(v-m),0)/(a.length-1) : 0;
const sdSample = (a)=> a.length>1 ? Math.sqrt(variance(a)) : 0;
const median = (a)=> { if(!a.length) return 0; const v=[...a].sort((p,q)=>p-q); const m=Math.floor(v.length/2); return v.length%2 ? v[m] : (v[m-1]+v[m])/2; };
const summarize = (arr)=> (!arr || !arr.length) ? { n:0, mean:0, sd:0, min:"—", median:0, max:"—" } : ({
  n: arr.length, mean: mean(arr), sd: sdSample(arr),
  min: Math.min(...arr), median: median(arr), max: Math.max(...arr)
});
const etaSquared = (SSb, SSt) => SSt ? SSb/SSt : 0;
const omegaSquared = (SSb, dfb, MSe, SSt) => (SSt + MSe) ? (SSb - dfb*MSe)/(SSt + MSe) : 0;

/** ====== NUEVO: Tukey (aprox Sidák) en front ====== **/
// asignación compacta de letras a partir de pares “significativos”
function compactLettersFromReject(pairsReject, groupOrder, meansDict) {
  const order = [...groupOrder].sort((a,b)=>(meansDict[b]??0)-(meansDict[a]??0));
  const bins = [];
  for (const g of order) {
    let placed = false;
    for (const set of bins) {
      let conflict = false;
      for (const h of set) {
        if (pairsReject.has(`${g}|||${h}`) || pairsReject.has(`${h}|||${g}`)) { conflict = true; break; }
      }
      if (!conflict) { set.add(g); placed = true; break; }
    }
    if (!placed) bins.push(new Set([g]));
  }
  const letters = {};
  const alpha = "abcdefghijklmnopqrstuvwxyz";
  const idxToLetters = (i)=>{ let s=""; let n=i; do{ s=alpha[n%26]+s; n=Math.floor(n/26)-1;}while(n>=0); return s; };
  bins.forEach((set,i)=>{ for (const g of set) letters[g]= (letters[g]||"") + idxToLetters(i); });
  return letters;
}

// cálculo de Tukey-Kramer aprox (Sidák) a partir de {grupo: [valores]}
function tukeyApproxFromGroups(groupMap, alpha=0.05) {
  const order = Object.keys(groupMap);
  const stats = {};
  let N = 0, k = 0, SSE = 0;

  for (const g of order) {
    const arr = (groupMap[g]||[]).filter(v=>Number.isFinite(v));
    const st = summarize(arr);
    stats[g] = st;
    if (st.n>0) { N += st.n; k += 1; SSE += arr.reduce((s,v)=> s + Math.pow(v - st.mean, 2), 0); }
  }
  if (k < 2) return null;
  const df_error = N - k;
  if (df_error <= 0) return null;
  const MSE = SSE / df_error;

  const m = (k*(k-1))/2;                               // # pares
  const alpha_pair = 1 - Math.pow(1 - alpha, 1/m);     // Sidák por par
  const tcrit = jStat.studentt.inv(1 - alpha_pair/2, df_error);
  const qcrit = Math.SQRT2 * tcrit;

  const pairs = [];
  const pairsReject = new Set();
  for (let i=0;i<order.length;i++){
    for (let j=i+1;j<order.length;j++){
      const g1 = order[i], g2 = order[j];
      const n1 = stats[g1].n, n2 = stats[g2].n;
      if (n1===0 || n2===0) continue;
      const diff = stats[g1].mean - stats[g2].mean;
      const se = Math.sqrt(MSE/2 * (1/n1 + 1/n2));
      if (!Number.isFinite(se) || se===0) continue;

      const q = Math.abs(diff)/se;
      const t = q/Math.SQRT2;
      const p_pair = 2*(1 - jStat.studentt.cdf(Math.abs(t), df_error));
      const p_adj = 1 - Math.pow(1 - Math.min(1, p_pair), m);
      const reject = q > qcrit; // equivalente a p_adj < alpha con esta aprox

      if (reject) pairsReject.add(`${g1}|||${g2}`);

      const margin = qcrit * se;
      pairs.push({
        g1, g2,
        meandiff: diff,
        q,
        lower: diff - margin,
        upper: diff + margin,
        p_adj: p_adj,
        reject
      });
    }
  }

  const meansDict = Object.fromEntries(order.map(g=>[g, stats[g].mean]));
  const letters = compactLettersFromReject(pairsReject, order, meansDict);

  return { mse: MSE, df_error, k, N, stats, order, pairs, letters, qcrit };
}

// plugin para pintar letras sobre barras/boxplots
const TukeyLettersPlugin = (lettersMap) => ({
  id: 'tukeyLetters',
  afterDatasetsDraw(chart) {
    const { ctx } = chart;
    const meta = chart.getDatasetMeta(0);
    if (!meta) return;
    ctx.save();
    ctx.textAlign = 'center';
    ctx.font = 'bold 12px sans-serif';

    chart.data.labels.forEach((label, i) => {
      const el = meta.data?.[i];
      if (!el) return;
      const pos = typeof el.tooltipPosition === 'function' ? el.tooltipPosition() : {x: el.x, y: el.y};
      const txt = lettersMap[label] || '';
      if (txt) ctx.fillText(txt, pos.x, pos.y - 8);
    });
    ctx.restore();
  }
});
/** ====== /Tukey ====== **/

export default {
  name: "AnovaAvanzada",
  setup() {
    // Estado base
    const estanques = ref([]);
    const todasSiembras = ref([]);
    const crecimiento = ref([]);
    const rubros = ref([]);
    const calidad = ref([]);

    // Selección
    const fuente = ref("crecimiento");
    const variableSeleccionada = ref("");
    const periodoSemanas = ref("all");
    const alpha = ref(0.05);

    const siembrasSeleccionadas = ref([]);
    const asignacionGrupo = ref({});
    const GRUPO_MAX = 10;

    // UI
    const expandido = ref({});
    const busquedaEstanque = ref("");
    const busquedaSiembra = ref({});

    // Charts/Resultados
    const chart = ref(null);
    const semanaGrafico = ref(1);
    const semanasDisponibles = ref([]);
    const resultadosSemanales = ref([]);
    const resumen = ref(null);

    // Datos crudos y stats usados para el ANOVA
    const rawByWeekGroup = ref({});
    const rawGlobalByGroup = ref({});
    const statsByWeekGroup = ref({});
    const statsGlobalByGroup = ref({});

    // ===== NUEVO: resultados de Tukey (por semana y global) =====
    const tukeyByWeek = ref({});   // { [wk]: { letters, stats, pairs, order, ... } }
    const tukeyGlobal = ref(null);

    // Variables disponibles
    const variablesDisponibles = computed(() => {
      if (fuente.value === "crecimiento") {
        return rubros.value.map(r => ({
          key: `rubro:${r.id_rubro}`,
          label: `${r.nombre} (${r.unidad})`,
          tipo: "rubro",
          id: r.id_rubro
        }));
      }
      const map = [
        ["temperatura","Temperatura","°C"],
        ["oxigeno_disuelto","Oxígeno disuelto","mg/L"],
        ["ph","pH",""],
        ["nitritos","Nitritos","mg/L"],
        ["nitratos","Nitratos","mg/L"],
        ["sulfato","Sulfato","mg/L"],
        ["fosfato","Fosfato","mg/L"],
        ["cloro","Cloro","mg/L"],
        ["salinidad","Salinidad","ppt"],
      ];
      return map.map(([key,label,unit])=>({key:`param:${key}`,label:`${label}${unit?` (${unit})`:''}`,tipo:"param",id:key}));
    });
    const labelVariable = computed(() => {
      const opt = variablesDisponibles.value.find(o=>o.key===variableSeleccionada.value);
      return opt ? opt.label : "";
    });

    // Grupos (UI)
    const grupos = computed(()=>{
      const base = new Map(Array.from({length:GRUPO_MAX}, (_,i)=>[i+1,[]]));
      siembrasSeleccionadas.value.forEach(id=>{
        const g = asignacionGrupo.value[id];
        if (g && base.has(g)) base.get(g).push(id);
      });
      return Array.from(base, ([gid, ids]) => ({ gid, ids }));
    });
    const puedeEjecutar = computed(()=>{
      const groups = grupos.value.filter(g=>g.ids.length);
      return variableSeleccionada.value && siembrasSeleccionadas.value.length>0 && groups.length>=2;
    });

    /** Backend **/
    const obtenerEstanques = async () => {
      const user = JSON.parse(localStorage.getItem("user")||"{}");
      const res = await axios.get("/estanque/");
      estanques.value = res.data.filter(e=> e.estatus && (!user || e.acuicola===user.acuicola));
    };
    const obtenerSiembras = async () => {
      const res = await axios.get("/siembra/");
      todasSiembras.value = res.data;
    };
    const obtenerCrecimiento = async () => {
      const [cres, rub] = await Promise.all([axios.get("/crecimiento/"), axios.get("/rubro/")]);
      crecimiento.value = cres.data;
      rubros.value = rub.data;
    };
    const obtenerCalidad = async () => {
      const res = await axios.get("/calidad-agua/");
      calidad.value = res.data;
    };

    /** Helpers selección **/
    const nombreEstanquePorId = computed(()=>{ const m = new Map(); estanques.value.forEach(e=>m.set(e.id_estanque,e.nombre)); return m; });
    const siembraPorId = computed(()=>{ const m = new Map(); todasSiembras.value.forEach(s=>m.set(s.id_siembra,s)); return m; });
    const etiquetaSiembra = (s)=>{ const est = nombreEstanquePorId.value.get(s.estanque) || s.estanque; return `${formatDate(s.fecha)} — ${s.especie} — ${est}`; };
    const nickSiembra = (sid)=>{ const s = siembraPorId.value.get(sid); if(!s) return `#${sid}`; const est = nombreEstanquePorId.value.get(s.estanque)||s.estanque; return `${formatDate(s.fecha)} ${s.especie} (${est})`; };

    const estanquesFiltrados = computed(()=>{ const q = busquedaEstanque.value.trim().toLowerCase(); if (!q) return estanques.value; return estanques.value.filter(e => (e.nombre||'').toLowerCase().includes(q)); });
    const siembrasDeEstanque = (eid)=> todasSiembras.value.filter(s=>s.estanque===eid);
    const siembrasDeEstanqueFiltradas = (eid)=>{ const q = (busquedaSiembra.value[eid]||'').trim().toLowerCase(); let arr = siembrasDeEstanque(eid); if (!q) return arr; return arr.filter(s=> etiquetaSiembra(s).toLowerCase().includes(q)); };
    const conteoSiembras = (eid)=> siembrasDeEstanque(eid).length;

    // UI actions
    const toggleExpand = (eid)=> { expandido.value[eid] = !expandido.value[eid]; };
    const seleccionarTodasDeEstanque = (eid)=>{ const ids = siembrasDeEstanqueFiltradas(eid).map(s=>s.id_siembra); const set = new Set([...siembrasSeleccionadas.value, ...ids]); siembrasSeleccionadas.value = Array.from(set); };
    const limpiarDeEstanque = (eid)=>{ const ids = new Set(siembrasDeEstanque(eid).map(s=>s.id_siembra)); siembrasSeleccionadas.value = siembrasSeleccionadas.value.filter(x=>!ids.has(x)); ids.forEach(id=> delete asignacionGrupo.value[id]); };
    const seleccionarTodasVisibles = ()=>{ const visibles=[]; for (const e of estanquesFiltrados.value) { visibles.push(...siembrasDeEstanqueFiltradas(e.id_estanque).map(s=>s.id_siembra)); } const set = new Set([...siembrasSeleccionadas.value, ...visibles]); siembrasSeleccionadas.value = Array.from(set); };
    const limpiarSeleccion = ()=>{ siembrasSeleccionadas.value=[]; asignacionGrupo.value={}; };
    const quitarSiembra = (sid)=>{ siembrasSeleccionadas.value=siembrasSeleccionadas.value.filter(x=>x!==sid); delete asignacionGrupo.value[sid]; };
    const grupoDeSiembra = (sid)=> asignacionGrupo.value[sid] || null;
    const toggleGrupo = (sid, g) => { if (asignacionGrupo.value[sid] === g) { delete asignacionGrupo.value[sid]; } else { asignacionGrupo.value[sid] = g; if (!siembrasSeleccionadas.value.includes(sid)) { siembrasSeleccionadas.value = [...siembrasSeleccionadas.value, sid]; } } };
    const removerDeGrupo = (sid)=>{ delete asignacionGrupo.value[sid]; };
    const vaciarGrupo = (g)=>{ Object.keys(asignacionGrupo.value).forEach(k=>{ if(asignacionGrupo.value[k]===g) delete asignacionGrupo.value[k]; }); };

    /** ANOVA principal **/
    async function ejecutarANOVA() {
      if (fuente.value==='crecimiento') await obtenerCrecimiento();
      else await obtenerCalidad();

      const seleccion = siembrasSeleccionadas.value.slice();
      if (!seleccion.length) return;

      const opt = variablesDisponibles.value.find(o=>o.key===variableSeleccionada.value);
      if (!opt) return;

      const getDate = (r)=> r.fecha;
      const getValue = (r)=>{
        if (fuente.value==='crecimiento') {
          if (r.rubro !== opt.id) return null;
          return r.medicion ?? null;
        } else {
          const v = r[opt.id];
          return (v==null||v==='') ? null : Number(v);
        }
      };

      function firstRecordTsBySiembra(sids) {
        const m = new Map();
        for (const sid of sids) {
          const arr = getAllRecordsForSiembra(sid);
          const filtered = arr.filter(r => getValue(r)!=null);
          if (!filtered.length) continue;
          const minT = Math.min(...filtered.map(r => Date.parse(getDate(r))));
          if (Number.isFinite(minT)) m.set(sid, minT);
        }
        return m;
      }
      function getAllRecordsForSiembra(sid) {
        if (fuente.value==='crecimiento') return crecimiento.value.filter(r=>r.siembra===sid);
        return calidad.value.filter(r=>r.siembra===sid);
      }

      const starts = firstRecordTsBySiembra(seleccion);

      const perWeekPerGroup = new Map(); // w -> Map("Grupo X" -> number[])
      const gruposTrabajo = grupos.value.filter(g=>g.ids.length).map(g=>({name:`Grupo ${g.gid}`, ids:g.ids}));

      let globalMaxW = 0;
      const pool = (fuente.value==='crecimiento') ? crecimiento.value : calidad.value;
      for (const r of pool) {
        if (!seleccion.includes(r.siembra)) continue;
        const start = starts.get(r.siembra);
        if (start==null) continue;
        const v = getValue(r);
        if (v==null || Number.isNaN(v)) continue;
        const ts = Date.parse(getDate(r));
        if (!Number.isFinite(ts)) continue;

        const w = Math.floor((ts - start)/MSW) + 1;
        if (w<1) continue;
        globalMaxW = Math.max(globalMaxW, w);

        const gid = asignacionGrupo.value[r.siembra];
        if (!gid) continue;
        const gname = `Grupo ${gid}`;

        let mapG = perWeekPerGroup.get(w);
        if (!mapG) { mapG = new Map(); perWeekPerGroup.set(w, mapG); }
        const arr = mapG.get(gname) || [];
        arr.push(Number(v));
        mapG.set(gname, arr);
      }

      let startW = 1, endW = globalMaxW;
      if (periodoSemanas.value !== 'all') {
        const N = Number(periodoSemanas.value);
        startW = Math.max(1, globalMaxW - N + 1);
      }

      const rows = [];
      const semanas = [];
      const rawWeekObj = {};
      for (let w=startW; w<=endW; w++) {
        const mapG = perWeekPerGroup.get(w) || new Map();
        const weekRow = {};
        for (const g of gruposTrabajo) weekRow[g.name] = (mapG.get(g.name) || []).slice();
        rawWeekObj[w] = weekRow;

        const gruposVals = Object.values(weekRow);
        const gruposConDatos = gruposVals.filter(a=>a.length>0).length;
        if (gruposConDatos < 2) continue;

        const { F, p, eta2, omega2, k, n } = anovaOneWay(gruposVals);
        rows.push({ week:w, F, p, eta2, omega2, k, n });
        semanas.push(w);
      }

      resultadosSemanales.value = rows;
      semanasDisponibles.value = semanas.length? semanas : [1];
      semanaGrafico.value = semanasDisponibles.value.at(-1) || 1;

      // Global crudo + stats
      const rawGlobal = {}; for (const g of gruposTrabajo) rawGlobal[g.name] = [];
      for (const [w, mapG] of perWeekPerGroup.entries()) {
        if (w < startW) continue;
        for (const g of gruposTrabajo) {
          const arr = (mapG.get(g.name) || []);
          rawGlobal[g.name].push(...arr);
        }
      }

      // Stats semanales y global
      const weeklyStats = {};
      for (const [wk, groupMap] of Object.entries(rawWeekObj)) {
        const row = {};
        for (const [gName, arr] of Object.entries(groupMap)) row[gName] = summarize(arr);
        weeklyStats[wk] = row;
      }
      const globalStats = {};
      for (const [gName, arr] of Object.entries(rawGlobal)) globalStats[gName] = summarize(arr);

      rawByWeekGroup.value = rawWeekObj;
      rawGlobalByGroup.value = rawGlobal;
      statsByWeekGroup.value = weeklyStats;
      statsGlobalByGroup.value = globalStats;

      // Resumen global ANOVA
      const globalVals = Object.values(rawGlobal).filter(a=>a.length>0);
      const global = globalVals.length>=2 ? anovaOneWay(globalVals) : {F:null,p:null,eta2:null,omega2:null,k:globalVals.length,n:globalVals.reduce((s,a)=>s+a.length,0)};
      resumen.value = { global };

      // ===== NUEVO: calcular Tukey (por semana y global) =====
      tukeyByWeek.value = {};
      for (const wk of semanasDisponibles.value) {
        const res = tukeyApproxFromGroups(rawByWeekGroup.value[wk], alpha.value);
        if (res) tukeyByWeek.value[wk] = res;
      }
      tukeyGlobal.value = tukeyApproxFromGroups(rawGlobalByGroup.value, alpha.value);

      await nextTick();
      renderChartForWeek();
    }

    function anovaOneWay(groups) {
      const k = groups.length;
      const n = groups.reduce((s,a)=>s+a.length,0);
      const all = groups.flat();

      const grandMean = mean(all);
      const SSb = groups.reduce((s, g)=> s + g.length * Math.pow(mean(g)-grandMean,2), 0);
      const SSw = groups.reduce((s, g)=> s + (g.length>1 ? (g.length-1)*variance(g) : 0), 0);
      const SSt = SSb + SSw;

      const dfb = k-1;
      const dfw = n-k;
      const MSb = dfb>0 ? SSb/dfb : 0;
      const MSw = dfw>0 ? SSw/dfw : 0;
      const F = (MSw>0) ? MSb/MSw : NaN;

      const p = Number.isFinite(F) ? (1 - fcdf(F, dfb, dfw)) : NaN;
      const eta2 = etaSquared(SSb, SSt);
      const omega2v = omegaSquared(SSb, dfb, MSw, SSt);

      return { F, p, eta2, omega2: omega2v, k, n };
    }

    async function renderChartForWeek() {
      if (!resumen.value || !resultadosSemanales.value.length) return;

      const weeksWithData = new Set(resultadosSemanales.value.map(r => r.week));
      let w = semanaGrafico.value;
      if (!weeksWithData.has(w)) { w = Math.max(...weeksWithData); semanaGrafico.value = w; }

      const labels = Object.keys(rawGlobalByGroup.value);
      const dataWeek = rawByWeekGroup.value[w] || {};
      const series = labels.map(l => dataWeek[l] || []);
      const totalObs = series.reduce((s, a) => s + a.length, 0);

      const el = document.getElementById("grafico-anova");
      if (!el) return;
      const wrap = el.parentElement;
      const h = wrap ? wrap.clientHeight : 480;
      el.height = h;

      const ctx = el.getContext("2d");
      if (chart.value) { chart.value.destroy(); chart.value = null; }

      const letters = (tukeyByWeek.value[w]?.letters) || {};
      const lettersPlugin = TukeyLettersPlugin(letters);

      if (!totalObs) {
        chart.value = new Chart(ctx, {
          type: "bar",
          data: { labels, datasets: [{ label: `Sin datos en Semana ${w}`, data: labels.map(() => 0) }] },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } }, scales: { y: { display: false } } },
          plugins: [lettersPlugin]
        });
        return;
      }

      const hasBoxplot = !!Chart.registry?.getController?.("boxplot");

      if (hasBoxplot) {
        chart.value = new Chart(ctx, {
          type: "boxplot",
          data: { labels, datasets: [{ label: `Observaciones crudas — Semana ${w}`, data: series, outlierRadius: 2, borderWidth: 1 }]},
          options: {
            responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } },
            scales: { x: { title: { display: true, text: "Grupo" } }, y: { title: { display: true, text: labelVariable.value }, beginAtZero: false } }
          },
          plugins: [lettersPlugin]
        });
      } else {
        const medias = series.map(a => a.length ? (a.reduce((s,v)=>s+v,0)/a.length) : 0);
        chart.value = new Chart(ctx, {
          type: "bar",
          data: { labels, datasets: [{ label: `Media — Semana ${w}`, data: medias, backgroundColor: "rgba(40,167,69,0.2)", borderColor: "#28a745", borderWidth: 1.5 }]},
          options: {
            responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } },
            scales: { x: { title: { display: true, text: "Grupo" } }, y: { title: { display: true, text: labelVariable.value }, beginAtZero: false } }
          },
          plugins: [lettersPlugin]
        });
      }
    }

    // ===== PDF / Excel (añadimos Tukey) =====
    const showPreview = ref(false);
    const previewUrl = ref(null);

    function buildTablesForPDF(doc, M, PAGE_H, PAGE_W) {
      // ANOVA semanal
      const head1 = [["Semana","k","N","F","p","η²","ω²","Signif. (α="+alpha.value+")"]];
      const body1 = resultadosSemanales.value.map(r => [
        `Semana ${r.week}`, String(r.k), String(r.n),
        fmt(r.F,4), fmt(r.p,4), fmt(r.eta2,4), fmt(r.omega2,4),
        r.p < alpha.value ? "Sí" : "No"
      ]);
      autoTable(doc, { startY: 120, margin: { left: M, right: M }, head: head1, body: body1, styles: { font: "helvetica", fontSize: 9, cellPadding: 4 }, headStyles: { fillColor: [240,240,240] } });

      // ANOVA global
      const g = resumen.value.global;
      autoTable(doc, {
        startY: doc.lastAutoTable.finalY + 14, margin: { left: M, right: M },
        head: [["k","N","F","p","η²","ω²","Signif. (α="+alpha.value+")"]],
        body: [[String(g.k), String(g.n), fmt(g.F,4), fmt(g.p,4), fmt(g.eta2,4), fmt(g.omega2,4), g.p < alpha.value ? "Sí":"No"]],
        styles: { font: "helvetica", fontSize: 9, cellPadding: 4 }, headStyles: { fillColor: [220,235,220] }
      });

      // ===== NUEVO: Tukey Semana Seleccionada =====
      const wk = semanaGrafico.value;
      const tk = tukeyByWeek.value[wk];
      if (tk) {
        autoTable(doc, { startY: doc.lastAutoTable.finalY + 18, margin: { left: M, right: M }, head: [[`Tukey-Kramer (aprox. Sidák) — Semana ${wk}`]], body: [], theme: "plain", styles: { fontStyle: "bold" }});
        const headT1 = [["Grupo","n","Media","DE","Letra"]];
        const bodyT1 = tk.order.map(g=>[g, tk.stats[g].n, fmt(tk.stats[g].mean,3), fmt(tk.stats[g].sd,3), tk.letters[g]]);
        autoTable(doc, { startY: doc.lastAutoTable.finalY + 2, margin: { left: M, right: M }, head: headT1, body: bodyT1, styles: { font: "helvetica", fontSize: 9, cellPadding: 4 }});
        if (tk.pairs.length) {
          const headT2 = [["Par","Δ medias","q","IC 95% aprox","p_adj aprox","Rechaza"]];
          const bodyT2 = tk.pairs.map(p=>[
            `${p.g1} vs ${p.g2}`, fmt(p.meandiff,4), fmt(p.q,4),
            `[${fmt(p.lower,4)}, ${fmt(p.upper,4)}]`,
            fmt(p.p_adj,4), p.reject?"Sí":"No"
          ]);
          autoTable(doc, { startY: doc.lastAutoTable.finalY + 8, margin: { left: M, right: M }, head: headT2, body: bodyT2, styles: { font: "helvetica", fontSize: 9, cellPadding: 4 }});
        }
      }

      // ===== NUEVO: Tukey Global =====
      if (tukeyGlobal.value) {
        const tg = tukeyGlobal.value;
        autoTable(doc, { startY: doc.lastAutoTable.finalY + 18, margin: { left: M, right: M }, head: [["Tukey-Kramer Global (aprox. Sidák)"]], body: [], theme: "plain", styles: { fontStyle: "bold" }});
        const headTG1 = [["Grupo","n","Media","DE","Letra"]];
        const bodyTG1 = tg.order.map(g=>[g, tg.stats[g].n, fmt(tg.stats[g].mean,3), fmt(tg.stats[g].sd,3), tg.letters[g]]);
        autoTable(doc, { startY: doc.lastAutoTable.finalY + 2, margin: { left: M, right: M }, head: headTG1, body: bodyTG1, styles: { font: "helvetica", fontSize: 9, cellPadding: 4 }});

        if (tg.pairs.length) {
          const headTG2 = [["Par","Δ medias","q","IC 95% aprox","p_adj aprox","Rechaza"]];
          const bodyTG2 = tg.pairs.map(p=>[
            `${p.g1} vs ${p.g2}`, fmt(p.meandiff,4), fmt(p.q,4),
            `[${fmt(p.lower,4)}, ${fmt(p.upper,4)}]`,
            fmt(p.p_adj,4), p.reject?"Sí":"No"
          ]);
          autoTable(doc, { startY: doc.lastAutoTable.finalY + 8, margin: { left: M, right: M }, head: headTG2, body: bodyTG2, styles: { font: "helvetica", fontSize: 9, cellPadding: 4 }});
        }
      }

      // ===== Stats Globales =====
      autoTable(doc, { startY: doc.lastAutoTable.finalY + 18, margin: { left: M, right: M }, head: [["Stats Globales"]], body: [], theme: "plain", styles: { fontStyle: "bold" }});
      const headG = [["Grupo","n","Media","DE","Mín","Mediana","Máx","Crudos (resumen)"]];
      const bodyG = Object.keys(statsGlobalByGroup.value).map(k => {
        const st = statsGlobalByGroup.value[k] || {};
        const raw = (rawGlobalByGroup.value[k] || []).join(", ");
        const resumido = raw.length > 200 ? raw.slice(0,200)+"…" : (raw || "—");
        return [k, st.n ?? 0, fmt(st.mean,3), fmt(st.sd,3), st.min ?? "—", fmt(st.median,3), st.max ?? "—", resumido];
      });
      autoTable(doc, { startY: doc.lastAutoTable.finalY + 2, margin: { left: M, right: M }, head: headG, body: bodyG, styles: { font: "helvetica", fontSize: 9, cellPadding: 4 }, columnStyles: { 7: { cellWidth: PAGE_W - 2*M - 400 } } });

      // ===== Stats Semana seleccionada =====
      const statsW = statsByWeekGroup.value[wk] || {};
      autoTable(doc, { startY: doc.lastAutoTable.finalY + 14, margin: { left: M, right: M }, head: [[`Stats Semana ${wk}`]], body: [], theme: "plain", styles: { fontStyle: "bold" }});
      const headW = [["Grupo","n","Media","DE","Mín","Mediana","Máx","Crudos (resumen)"]];
      const bodyW = Object.keys(rawGlobalByGroup.value).map(k => {
        const st = statsW[k] || {};
        const raw = ((rawByWeekGroup.value[wk]||{})[k] || []).join(", ");
        const resumido = raw.length > 200 ? raw.slice(0,200)+"…" : (raw || "—");
        return [k, st.n ?? 0, fmt(st.mean,3), fmt(st.sd,3), st.min ?? "—", fmt(st.median,3), st.max ?? "—", resumido];
      });
      autoTable(doc, { startY: doc.lastAutoTable.finalY + 2, margin: { left: M, right: M }, head: headW, body: bodyW, styles: { font: "helvetica", fontSize: 9, cellPadding: 4 }, columnStyles: { 7: { cellWidth: PAGE_W - 2*M - 400 } } });
    }

    async function construirPDF({preview=false}={}) {
      const doc = new jsPDF({ orientation: "portrait", unit: "pt", format: "a4" });
      const M = 44; const W = doc.internal.pageSize.getWidth(); const H = doc.internal.pageSize.getHeight();
      const setFont = (f="helvetica", s=10, st="normal") => { doc.setFont(f, st); doc.setFontSize(s); };

      setFont("helvetica", 16, "bold");
      doc.text("ANOVA de un factor — por semanas", M, M+6);
      setFont("helvetica", 10);
      doc.setTextColor(120); doc.text(`Generado: ${formatDate(new Date())}`, W - M, M+6, {align:"right"});
      doc.setTextColor(0); doc.setDrawColor(230); doc.line(M, M+12, W-M, M+12);

      // Resumen
      setFont("helvetica", 11, "bold"); doc.text("Resumen", M, M+28);
      setFont("helvetica", 10);
      const opt = variablesDisponibles.value.find(o=>o.key===variableSeleccionada.value);
      const periodTxt = periodoSemanas.value==='all' ? "Completo" : `Últimas ${periodoSemanas.value} semanas`;
      const resumenL = [
        `Fuente: ${fuente.value==='crecimiento'?'Crecimiento':'Calidad de Agua'}`,
        `Variable: ${opt?opt.label:''}`,
        `Periodo: ${periodTxt}`,
        `Agrupación: Grupos manuales (1..10)`,
        `α: ${alpha.value}`,
        `Post-hoc: Tukey-Kramer (aprox. Sidák) en front`
      ];
      let y = M+28+12;
      resumenL.forEach(line=>{ doc.text(line, M, y); y+=12; });

      // Gráfico
      const canvas = document.getElementById("grafico-anova");
      if (canvas) {
        const img = canvas.toDataURL("image/png", 1.0);
        const CH = 220;
        doc.addImage(img, "PNG", M, y+4, W - 2*M, CH, "", "FAST");
        y += CH + 18;
      }

      // Tablas (incluye Tukey)
      buildTablesForPDF(doc, M, H, W);

      // Footer
      const pages = doc.getNumberOfPages();
      for (let i=1;i<=pages;i++) { doc.setPage(i); setFont("helvetica",9); doc.setTextColor(120); doc.text(`Página ${i} de ${pages}`, W/2, H-12, {align:"center"}); doc.setTextColor(0); }

      if (preview) {
        const blob = doc.output("blob"); const url = URL.createObjectURL(blob); return url;
      } else {
        doc.save(`anova_${fuente.value}_${Date.now()}.pdf`); return null;
      }
    }

    async function mostrarVistaPrevia() {
      if (!resumen.value || !resultadosSemanales.value.length) return;
      const url = await construirPDF({ preview: true });
      previewUrl.value = url;
      showPreview.value = true;
    }
    function cerrarPreview() { showPreview.value = false; if (previewUrl.value) { URL.revokeObjectURL(previewUrl.value); previewUrl.value=null; } }
    function exportarPDF(){ construirPDF({preview:false}); }

    function exportarExcel() {
      import("xlsx").then(XLSX => {
        const wb = XLSX.utils.book_new();

        // Hoja 1: ANOVA
        const rows1 = [];
        rows1.push(["ANOVA semanal"]);
        rows1.push(["Semana","k","N","F","p","eta2","omega2","Signif (α="+alpha.value+")"]);
        resultadosSemanales.value.forEach(r=>{
          rows1.push([r.week, r.k, r.n, r.F, r.p, r.eta2, r.omega2, r.p < alpha.value ? "Sí":"No"]);
        });
        rows1.push([]);
        rows1.push(["ANOVA global"]);
        rows1.push(["k","N","F","p","eta2","omega2","Signif (α="+alpha.value+")"]);
        const g = resumen.value.global;
        rows1.push([g.k, g.n, g.F, g.p, g.eta2, g.omega2, g.p < alpha.value ? "Sí":"No"]);
        const ws1 = XLSX.utils.aoa_to_sheet(rows1);
        XLSX.utils.book_append_sheet(wb, ws1, "ANOVA");

        // Hoja 2: Stats Globales
        const rowsG = [["Grupo","n","Media","DE","Min","Mediana","Max"]];
        for (const k of Object.keys(statsGlobalByGroup.value)) {
          const st = statsGlobalByGroup.value[k];
          rowsG.push([k, st.n, st.mean, st.sd, st.min, st.median, st.max]);
        }
        const ws2 = XLSX.utils.aoa_to_sheet(rowsG);
        XLSX.utils.book_append_sheet(wb, ws2, "Stats Global");

        // Hoja 3: Stats Semanales
        const rowsS = [["Semana","Grupo","n","Media","DE","Min","Mediana","Max"]];
        for (const wk of semanasDisponibles.value) {
          const rowStats = statsByWeekGroup.value[wk] || {};
          for (const gname of Object.keys(rawGlobalByGroup.value)) {
            const st = rowStats[gname] || { n:0, mean:0, sd:0, min:"", median:"", max:"" };
            rowsS.push([wk, gname, st.n, st.mean, st.sd, st.min, st.median, st.max]);
          }
        }
        const ws3 = XLSX.utils.aoa_to_sheet(rowsS);
        XLSX.utils.book_append_sheet(wb, ws3, "Stats Semanales");

        // Hoja 4: Raw
        const rowsR = [["Nivel","Semana","Grupo","Valor"]];
        for (const [gname, arr] of Object.entries(rawGlobalByGroup.value)) for (const v of arr) rowsR.push(["Global","",gname,v]);
        for (const wk of semanasDisponibles.value) {
          const weekRow = rawByWeekGroup.value[wk] || {};
          for (const [gname, arr] of Object.entries(weekRow)) for (const v of arr) rowsR.push(["Semana", wk, gname, v]);
        }
        const ws4 = XLSX.utils.aoa_to_sheet(rowsR);
        XLSX.utils.book_append_sheet(wb, ws4, "Raw");

        // ===== NUEVO: Hoja 5: Tukey Semana seleccionada =====
        const tks = tukeyByWeek.value[semanaGrafico.value];
        if (tks) {
          const rowsT1 = [["Grupo","n","Media","DE","Letra"]];
          tks.order.forEach(g=> rowsT1.push([g, tks.stats[g].n, tks.stats[g].mean, tks.stats[g].sd, tks.letters[g]]));
          const ws5 = XLSX.utils.aoa_to_sheet(rowsT1);
          XLSX.utils.book_append_sheet(wb, ws5, `Tukey_Sem_${semanaGrafico.value}`);

          const rowsT2 = [["Par","Δ medias","q","IC 95% aprox (inf)","IC 95% aprox (sup)","p_adj aprox","Rechaza"]];
          tks.pairs.forEach(p => rowsT2.push([`${p.g1} vs ${p.g2}`, p.meandiff, p.q, p.lower, p.upper, p.p_adj, p.reject?"Sí":"No"]));
          const ws5b = XLSX.utils.aoa_to_sheet(rowsT2);
          XLSX.utils.book_append_sheet(wb, ws5b, `Tukey_Sem_${semanaGrafico.value}_pares`);
        }

        // ===== NUEVO: Hoja 6: Tukey Global =====
        if (tukeyGlobal.value) {
          const tg = tukeyGlobal.value;
          const rowsTG1 = [["Grupo","n","Media","DE","Letra"]];
          tg.order.forEach(g=> rowsTG1.push([g, tg.stats[g].n, tg.stats[g].mean, tg.stats[g].sd, tg.letters[g]]));
          const ws6 = XLSX.utils.aoa_to_sheet(rowsTG1);
          XLSX.utils.book_append_sheet(wb, ws6, `Tukey_Global`);

          const rowsTG2 = [["Par","Δ medias","q","IC 95% aprox (inf)","IC 95% aprox (sup)","p_adj aprox","Rechaza"]];
          tg.pairs.forEach(p => rowsTG2.push([`${p.g1} vs ${p.g2}`, p.meandiff, p.q, p.lower, p.upper, p.p_adj, p.reject?"Sí":"No"]));
          const ws6b = XLSX.utils.aoa_to_sheet(rowsTG2);
          XLSX.utils.book_append_sheet(wb, ws6b, `Tukey_Global_pares`);
        }

        XLSX.writeFile(wb, `anova_${fuente.value}_${Date.now()}.xlsx`);
      });
    }

    // Watchers
    watch(semanaGrafico, async () => { if (!resumen.value) return; await nextTick(); renderChartForWeek(); });
    watch(resultadosSemanales, async () => { if (!resumen.value) return; await nextTick(); renderChartForWeek(); });

    onMounted(async ()=>{ await Promise.all([obtenerEstanques(), obtenerSiembras(), obtenerCrecimiento(), obtenerCalidad()]); });

    return {
      // selects
      fuente, variableSeleccionada, variablesDisponibles, periodoSemanas, alpha, labelVariable,

      // ponds/seeds
      estanques, todasSiembras, expandido, busquedaEstanque, busquedaSiembra,
      estanquesFiltrados, siembrasDeEstanqueFiltradas, conteoSiembras, etiquetaSiembra, nickSiembra,

      // selection/groups
      siembrasSeleccionadas, asignacionGrupo, GRUPO_MAX,
      toggleExpand, seleccionarTodasDeEstanque, limpiarDeEstanque,
      seleccionarTodasVisibles, limpiarSeleccion, quitarSiembra,
      grupoDeSiembra, toggleGrupo, removerDeGrupo, vaciarGrupo,
      grupos, puedeEjecutar,

      // results
      ejecutarANOVA, resultadosSemanales, resumen, semanaGrafico, semanasDisponibles,
      fmt,

      // datos crudos / stats
      rawByWeekGroup, rawGlobalByGroup, statsByWeekGroup, statsGlobalByGroup,

      // Tukey
      tukeyByWeek, tukeyGlobal,

      // chart
      renderChartForWeek,

      // pdf/excel
      mostrarVistaPrevia, cerrarPreview, exportarPDF, exportarExcel,
      showPreview, previewUrl,
    };
  },
};
</script>

<style scoped>
/* (todo tu CSS tal cual) */
.grafico-container {
  font-family: 'Poppins', sans-serif;
  max-width: 100%;
  margin: 30px auto;
  padding: 25px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
  transition: all .3s ease-in-out;
}
h1 { margin: 0 0 12px 0; font-weight: 700; font-size: 22px; color: #1d1d1f; }
.form-seleccion.one-col { display: flex; flex-direction: column; gap: 12px; margin-bottom: 12px; }
label { font-weight: 600; margin-bottom: 6px; color: #444; font-size: 14px; }
select, input[type="number"], .input {
  width: 100%; padding: 12px; box-sizing: border-box; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; background: #f8f9fa; transition: all .2s ease;
}
select:focus, input[type="number"]:focus, .input:focus { border-color: #28a745; outline: none; box-shadow: 0 0 0 3px rgba(40,167,69,.15); }
.card { border: 1px solid #eee; border-radius: 12px; padding: 12px; margin-top: 12px; background: #fff; }
.card.inner { margin-top: 12px; }
.block-title { display: block; margin-bottom: 8px; font-weight: 700; color: #1d1d1f; }
.toolbar-top { display: flex; flex-direction: column; gap: 8px; padding: 12px; margin-bottom: 12px; border: 1px solid #eee; border-radius: 12px; background: #fbfffc; }
.row { display: flex; gap: 12px; flex-wrap: wrap; }
.col { min-width: 220px; flex: 1; display: flex; flex-direction: column; }
.list { list-style: none; padding: 0; margin: 0; }
.pond-row { border: 1px solid #eee; border-radius: 10px; padding: 10px; margin-bottom: 10px; background: #fff; }
.pond-row-main { display: flex; justify-content: space-between; align-items: center; cursor: pointer; padding: 6px 4px; border-radius: 8px; }
.pond-row-main:hover { background: #f8fff9; }
.pond-name { font-weight: 600; color: #1d1d1f; }
.pond-meta { display: flex; gap: 10px; align-items: center; }
.meta { color: #666; font-size: 12px; }
.chev { color: #28a745; font-weight: 700; }
.siembras-panel { margin-top: 10px; padding-top: 10px; border-top: 1px dashed #e5e5e5; }
.panel-actions { display: flex; gap: 8px; margin-bottom: 8px; }
.siembras-list { max-height: 260px; overflow: auto; }
.siembras-list li { padding: 6px 0; border-bottom: 1px dashed #f0f0f0; display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.checkbox-label { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; }
.grp-buttons { display: inline-flex; gap: 4px; flex-wrap: wrap; }
.grp-btn { border: 1px solid #cfd; border-radius: 8px; padding: 4px 8px; font-size: 12px; min-width: 28px; background: #fff; color: #1d1d1f; cursor: pointer; transition: all .15s ease; }
.grp-btn:hover { background: #f3fff6; border-color: #28a745; }
.grp-btn.active { background: #eaffef; border-color: #28a745; color: #176f34; font-weight: 700; box-shadow: 0 0 0 3px rgba(40,167,69,.12) inset; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; margin: 6px 0 10px; }
.chip { background: #f0fff4; border: 1px solid #d1f5dc; color: #1d7f3b; padding: 6px 10px; border-radius: 999px; font-size: 12px; display: inline-flex; gap: 6px; align-items: center; }
.chip.tiny { font-size: 11px; padding: 4px 8px; }
.chip-x { background: transparent; border: none; cursor: pointer; font-size: 14px; line-height: 1; color: #1d7f3b; }
button { background-color: #28a745; color: white; border: none; padding: 12px 15px; font-size: 14px; cursor: pointer; border-radius: 8px; font-weight: 700; transition: all .2s ease-in-out; text-transform: uppercase; letter-spacing: .3px; display: inline-flex; align-items: center; justify-content: center; }
button:hover { background-color: #218838; transform: translateY(-1px); }
button:active { transform: translateY(0); }
.btn-cta { align-self: flex-end; }
.btn-sm { padding: 8px 10px; font-size: 12px; border-radius: 8px; }
.btn-sm.outline, .btn-generar.outline { background: #fff; color: #28a745; border: 1px solid #28a745; }
.btn-row { display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px; }
.stats-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; }
.stats-table th, .stats-table td { padding: 8px; border: 1px solid #ddd; text-align: center; }
.stats-table thead th { background: #f8f9fa; font-weight: 700; }
.chart-header { display: flex; align-items: center; justify-content: space-between; }
.chart-wrap { position: relative; width: 100%; height: clamp(420px, 60vh, 800px); }
.chart-wrap canvas { width: 100% !important; height: 100% !important; display: block; }
.muted { color: #777; font-size: 13px; }
.fade-enter-active, .fade-leave-active { transition: opacity .15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index: 9999; }
.modal { width: min(1000px, 92vw); height: min(85vh, 900px); background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,.2); display:flex; flex-direction: column; }
.modal-header { display:flex; align-items:center; justify-content:space-between; padding: 10px 14px; border-bottom: 1px solid #eee; }
.pdf-frame { width: 100%; height: 100%; border: 0; }
@media (max-width: 980px) { .grid-2 { grid-template-columns: 1fr; } }
</style>
