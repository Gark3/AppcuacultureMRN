<template>
  <div class="grafico-container">
    <h1>Calidad de Agua por Estanque (agregación semanal)</h1>

    <form class="form-seleccion one-col" @submit.prevent="actualizarGraficos">
    
    <div class="card block">
      <label class="toggle">
        <input type="checkbox" v-model="comparar" />
        <span>Comparar Siembras (hasta {{ GRUPO_MAX }} grupos)</span>
      </label>
    </div>
      <!-- Estanques + Siembras + Grupos -->
      <div class="card block">
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
                  :placeholder="`Buscar siembras de ${e.nombre} (fecha/especie)…`"
                />

                <ul class="siembras-list">
                  <li v-for="s in siembrasDeEstanqueFiltradas(e.id_estanque)" :key="s.id_siembra">
                    <label class="checkbox-label">
                      <input type="checkbox" :value="s.id_siembra" v-model="siembrasSeleccionadas" />
                      <span>{{ etiquetaSiembra(s) }}</span>
                    </label>

                    <div class="grp-buttons" v-if="comparar">
                      <button
                        v-for="g in GRUPO_MAX"
                        :key="g"
                        type="button"
                        class="grp-btn"
                        :class="{active: grupoDeSiembra(s.id_siembra)===g}"
                        @click="toggleGrupo(s.id_siembra,g)"
                        :title="`Asignar a Grupo ${g}`"
                      >{{ g }}</button>
                    </div>
                  </li>
                </ul>
              </div>
            </transition>
          </li>
        </ul>

        <!-- Resumen selección + grupos -->
        <div class="card block inner">
          <label class="block-title">Siembras seleccionadas</label>
          <div class="chips" v-if="siembrasSeleccionadas.length">
            <span class="chip" v-for="sid in siembrasSeleccionadas" :key="sid">
              {{ etiquetaSiembraPorId(sid) }}
              <button type="button" class="chip-x" @click="quitarSiembra(sid)">×</button>
            </span>
          </div>
          <div class="muted" v-else>Sin siembras seleccionadas.</div>

          <div class="quick-actions">
            <button type="button" class="btn-sm" @click="seleccionarTodasVisibles">Seleccionar visibles</button>
            <button type="button" class="btn-sm outline" @click="limpiarSeleccion">Limpiar</button>
          </div>

          <div v-if="comparar" class="grupos-summary">
            <div v-for="g in grupos" :key="g.gid" class="grupo-line" v-show="g.ids.length">
              <strong>Grupo {{ g.gid }}:</strong>
              <span class="chip tiny" v-for="sid in g.ids" :key="`G${g.gid}-${sid}`">
                {{ nickSiembra(sid) }}
                <button type="button" class="chip-x" @click="removerDeGrupo(sid)">×</button>
              </span>
              <button type="button" class="btn-sm outline" @click="vaciarGrupo(g.gid)">Vaciar {{ g.gid }}</button>
            </div>
            <div class="muted" v-if="!hayGruposConMiembros">Sin grupos con siembras.</div>
          </div>
        </div>
      </div>

      <!-- Periodo (semanas) + Parámetros (checkboxes) -->
      <div class="card block">
        <div class="form-group">
          <label for="periodo">Periodo</label>
          <select v-model="periodoSemanas" required>
            <option v-for="p in periodosSemanas" :key="p.value" :value="p.value">{{ p.label }}</option>
          </select>
          <small class="hint">
            Las semanas se cuentan desde el primer registro de cada siembra. Si una siembra no tiene datos en una semana, se promedia con lo disponible.
          </small>
        </div>

        <div class="form-group">
          <label>Parámetros</label>
          <div class="param-grid">
            <label v-for="p in parametrosActuales" :key="p" class="checkbox-label">
              <input type="checkbox" :value="p" v-model="parametrosSeleccionados" />
              <span>{{ p }} <small v-if="unidadDe(p)">({{ unidadDe(p) }})</small></span>
            </label>
          </div>
          <small class="hint">Selecciona uno o varios.</small>
        </div>

        <button
          type="submit"
          :disabled="siembrasSeleccionadas.length === 0 || parametrosSeleccionados.length === 0 || (comparar && !hayGruposConMiembros)"
          class="btn-cta"
        >
          Generar Gráfico(s)
        </button>
      </div>
    </form>

    <!-- Gráficos + Tablas de estadísticos -->
    <div v-if="parametrosSeleccionados.length">
      <div v-for="param in parametrosSeleccionados" :key="param" class="grafico-individual">
        <div class="chart-header">
          <h3>
            {{ param }} <small>({{ unidadDe(param) }})</small>
            <span v-if="siembrasSeleccionadas.length"> — {{ tituloSerie }}</span>
          </h3>
        </div>
        <div class="chart-wrap">
          <canvas :id="idCanvas(param)"></canvas>
        </div>

        <!-- Tablas de estadísticos por grupo -->
        <div class="stats-wrap" v-if="weeklyStats[param]">
          <div
            v-for="(rows, gname) in weeklyStats[param]"
            :key="`${param}-${gname}`"
            class="grafico-individual"
          >
            <h4 class="stats-title">Estadísticos — {{ gname }} — {{ param }} <small v-if="unidadDe(param)">({{ unidadDe(param) }})</small></h4>
            <table class="stats-table">
              <thead>
                <tr>
                  <th>Semana</th>
                  <th>n</th>
                  <th>Promedio</th>
                  <th>Desv. Est.</th>
                  <th>CV%</th>
                  <th>Mín</th>
                  <th>Mediana</th>
                  <th>Máx</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in rows" :key="`${gname}-${param}-${r.week}`">
                  <td>{{ toLabel(r.week) }}</td>
                  <td>{{ r.n }}</td>
                  <td>{{ fmt(r.mean) }}</td>
                  <td>{{ fmt(r.sd) }}</td>
                  <td>{{ fmt(r.cv) }}</td>
                  <td>{{ fmt(r.min) }}</td>
                  <td>{{ fmt(r.median) }}</td>
                  <td>{{ fmt(r.max) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>

    <!-- Botones PDF -->
    <div class="btn-row">
      <button type="button" class="btn-generar outline" @click="mostrarVistaPrevia" :disabled="parametrosSeleccionados.length===0">Vista previa PDF</button>
      <button type="button" class="btn-generar" @click="exportarReporte" :disabled="parametrosSeleccionados.length===0">Descargar PDF</button>
    </div>

    <!-- Modal vista previa PDF -->
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
import { ref, onMounted, computed, nextTick } from "vue";
import axios from "@/services/axios";
import Chart from "chart.js/auto";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

/** Utils **/
const MSW = 7 * 24 * 60 * 60 * 1000;
const formatDate = (d) => new Date(d).toISOString().split("T")[0];
const mean = (arr) => arr.reduce((a, b) => a + b, 0) / arr.length;
const median = (arr) => {
  const a = [...arr].sort((x, y) => x - y);
  const n = a.length;
  if (!n) return null;
  return n % 2 ? a[(n - 1) / 2] : (a[n / 2 - 1] + a[n / 2]) / 2;
};
const stdDevSample = (arr) => {
  const n = arr.length;
  if (n < 2) return null;
  const m = mean(arr);
  const s2 = arr.reduce((acc, v) => acc + (v - m) * (v - m), 0) / (n - 1);
  return Math.sqrt(s2);
};
const safeNum = (v) => (v == null || Number.isNaN(v) ? null : Number(v));
const toLabel = (w) => `Semana ${w}`;
const idCanvas = (param) =>
  `grafico-${
    String(param)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/\s+/g, "-")
      .toLowerCase()
  }`;
const fmt = (v, d = 2) => (v == null || Number.isNaN(v) ? "—" : Number(v).toFixed(d));

export default {
  name: "CalidadAguaSemanal",
  setup() {
    /** Estado base **/
    const estanques = ref([]);
    const todasSiembras = ref([]);
    const datos = ref([]); // /calidad-agua/

    /** Selección y UI **/
    const siembrasSeleccionadas = ref([]);
    const expandido = ref({});
    const busquedaEstanque = ref("");
    const busquedaSiembra = ref({});

    /** Comparación y grupos **/
    const GRUPO_MAX = 10;
    const comparar = ref(false);
    const asignacionGrupo = ref({}); // { [siembraId]: number 1..10 }
    const grupos = computed(() => {
      const base = new Map(Array.from({ length: GRUPO_MAX }, (_, i) => [i + 1, []]));
      siembrasSeleccionadas.value.forEach((id) => {
        const g = asignacionGrupo.value[id];
        if (g && base.has(g)) base.get(g).push(id);
      });
      return Array.from(base, ([gid, ids]) => ({ gid, ids }));
    });
    const hayGruposConMiembros = computed(() => grupos.value.some((g) => g.ids.length > 0));

    /** Parámetros y unidades **/
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
    const unidades = new Map([
      ["Temperatura", "°C"],
      ["Oxígeno disuelto", "mg/L"],
      ["pH", ""],
      ["Nitritos", "mg/L"],
      ["Nitratos", "mg/L"],
      ["Sulfato", "mg/L"],
      ["Fosfato", "mg/L"],
      ["Cloro", "mg/L"],
      ["Salinidad", "ppt"],
    ]);
    const unidadDe = (p) => unidades.get(p) ?? "";

    // Checkboxes de parámetros
    const parametrosSeleccionados = ref(["Temperatura", "Oxígeno disuelto", "pH"]);

    // Periodos por semanas
    const periodosSemanas = [
      { label: "Completo", value: "all" },
      { label: "Últimas 4 semanas", value: 4 },
      { label: "Últimas 8 semanas", value: 8 },
      { label: "Últimas 12 semanas", value: 12 },
    ];
    const periodoSemanas = ref("all");

    /** Instancias de charts **/
    const chartInstances = ref({});

    /** Estadísticos semanales por parámetro y grupo (para UI/PDF) **/
    // Estructura: weeklyStats.value[param] = { [groupName]: rows[] }
    // rows: {week, n, mean, sd, cv, min, median, max}
    const weeklyStats = ref({});

    /** Backend **/
    const obtenerEstanques = async () => {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      const res = await axios.get("/estanque/");
      estanques.value = res.data.filter((e) => e.estatus && (!user || e.acuicola === user.acuicola));
    };
    const obtenerTodasLasSiembras = async () => {
      const res = await axios.get("/siembra/");
      todasSiembras.value = res.data;
    };
    const obtenerCalidadAgua = async () => {
      const res = await axios.get("/calidad-agua/");
      datos.value = res.data;
    };

    /** Helpers siembras **/
    const nombreEstanquePorId = computed(() => {
      const m = new Map();
      estanques.value.forEach((e) => m.set(e.id_estanque, e.nombre));
      return m;
    });
    const siembraPorId = computed(() => {
      const m = new Map();
      todasSiembras.value.forEach((s) => m.set(s.id_siembra, s));
      return m;
    });
    const etiquetaSiembra = (s) => {
      const est = nombreEstanquePorId.value.get(s.estanque) || `Estanque ${s.estanque}`;
      return `${formatDate(s.fecha)} — ${s.especie} — ${est}`;
    };
    const etiquetaSiembraPorId = (id) => {
      const s = siembraPorId.value.get(id);
      return s ? etiquetaSiembra(s) : `Siembra ${id}`;
    };
    const nickSiembra = (id) => {
      const s = siembraPorId.value.get(id);
      if (!s) return `#${id}`;
      const est = nombreEstanquePorId.value.get(s.estanque) || s.estanque;
      return `${formatDate(s.fecha)} ${s.especie} (${est})`;
    };

    const firstDatoFecha = (siembraId) => {
      const arr = datos.value.filter((d) => d.siembra === siembraId);
      if (!arr.length) return "–";
      const minT = Math.min(...arr.map((d) => new Date(d.fecha).getTime()));
      return formatDate(new Date(minT));
    };
    const lastDatoFecha = (siembraId) => {
      const arr = datos.value.filter((d) => d.siembra === siembraId);
      if (!arr.length) return "–";
      const maxT = Math.max(...arr.map((d) => new Date(d.fecha).getTime()));
      return formatDate(new Date(maxT));
    };

    /** Filtros UI **/
    const estanquesFiltrados = computed(() => {
      const q = busquedaEstanque.value.trim().toLowerCase();
      if (!q) return estanques.value;
      return estanques.value.filter((e) => (e.nombre || "").toLowerCase().includes(q));
    });
    const siembrasDeEstanque = (estanqueId) => todasSiembras.value.filter((s) => s.estanque === estanqueId);
    const siembrasDeEstanqueFiltradas = (estanqueId) => {
      const q = (busquedaSiembra.value[estanqueId] || "").trim().toLowerCase();
      let arr = siembrasDeEstanque(estanqueId);
      if (!q) return arr;
      return arr.filter((s) => etiquetaSiembra(s).toLowerCase().includes(q));
    };
    const conteoSiembras = (estanqueId) => siembrasDeEstanque(estanqueId).length;

    /** Acciones UI **/
    const toggleExpand = (estanqueId) => {
      expandido.value[estanqueId] = !expandido.value[estanqueId];
    };
    const seleccionarTodasDeEstanque = (estanqueId) => {
      const ids = siembrasDeEstanqueFiltradas(estanqueId).map((s) => s.id_siembra);
      const set = new Set([...siembrasSeleccionadas.value, ...ids]);
      siembrasSeleccionadas.value = Array.from(set);
    };
    const limpiarDeEstanque = (estanqueId) => {
      const ids = new Set(siembrasDeEstanque(estanqueId).map((s) => s.id_siembra));
      siembrasSeleccionadas.value = siembrasSeleccionadas.value.filter((id) => !ids.has(id));
      ids.forEach((id) => {
        delete asignacionGrupo.value[id];
      });
    };
    const seleccionarTodasVisibles = () => {
      const visibles = [];
      for (const e of estanquesFiltrados.value) {
        visibles.push(...siembrasDeEstanqueFiltradas(e.id_estanque).map((s) => s.id_siembra));
      }
      const set = new Set([...siembrasSeleccionadas.value, ...visibles]);
      siembrasSeleccionadas.value = Array.from(set);
    };
    const limpiarSeleccion = () => {
      siembrasSeleccionadas.value = [];
      asignacionGrupo.value = {};
    };
    const quitarSiembra = (sid) => {
      siembrasSeleccionadas.value = siembrasSeleccionadas.value.filter((x) => x !== sid);
      delete asignacionGrupo.value[sid];
    };
    const grupoDeSiembra = (sid) => asignacionGrupo.value[sid] || null;
    const toggleGrupo = (sid, grupo) => {
      if (!siembrasSeleccionadas.value.includes(sid))
        siembrasSeleccionadas.value = [...siembrasSeleccionadas.value, sid];
      if (asignacionGrupo.value[sid] === grupo) delete asignacionGrupo.value[sid];
      else asignacionGrupo.value[sid] = grupo;
    };
    const removerDeGrupo = (sid) => {
      delete asignacionGrupo.value[sid];
    };
    const vaciarGrupo = (grupo) => {
      Object.keys(asignacionGrupo.value).forEach((k) => {
        if (asignacionGrupo.value[k] === grupo) delete asignacionGrupo.value[k];
      });
    };

    /** Normalización de campo backend **/
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

    /** Título **/
    const tituloSerie = computed(() => {
      if (!comparar.value) return `Promedio semanal de ${siembrasSeleccionadas.value.length} siembra(s)`;
      const gruposConCount = grupos.value.filter((g) => g.ids.length).map((g) => `G${g.gid}(${g.ids.length})`);
      return `Comparación semanal ${gruposConCount.join(" · ")}`;
    });

    /** CORE: Agregación semanal **/
    const firstRecordTsBySiembra = (siembrasIds) => {
      const m = new Map();
      for (const sid of siembrasIds) {
        const arr = datos.value.filter((d) => d.siembra === sid);
        if (!arr.length) continue;
        const minT = Math.min(...arr.map((d) => Date.parse(d.fecha)));
        if (Number.isFinite(minT)) m.set(sid, minT);
      }
      return m;
    };

    // sid -> Map(week -> avgSemanaDelCiclo) para un parámetro
    const weeklyAvgBySiembra = (siembrasIds, paramField) => {
      const starts = firstRecordTsBySiembra(siembrasIds);
      const perSiembraWeekVals = new Map(); // sid -> { week -> [vals] }

      for (const d of datos.value) {
        if (!siembrasIds.includes(d.siembra)) continue;
        const start = starts.get(d.siembra);
        if (start == null) continue;
        const v = safeNum(d[paramField]);
        if (v == null) continue;
        const ts = Date.parse(d.fecha);
        if (!Number.isFinite(ts)) continue;

        const w = Math.floor((ts - start) / MSW) + 1; // Semana 1 desde primer registro
        if (w < 1) continue;

        let mapW = perSiembraWeekVals.get(d.siembra);
        if (!mapW) {
          mapW = new Map();
          perSiembraWeekVals.set(d.siembra, mapW);
        }
        const arr = mapW.get(w) || [];
        arr.push(v);
        mapW.set(w, arr);
      }

      // Promedio semanal por siembra
      const perSiembraWeekAvg = new Map(); // sid -> Map(week -> avg)
      for (const [sid, mapW] of perSiembraWeekVals.entries()) {
        const avgMap = new Map();
        Array.from(mapW.keys())
          .sort((a, b) => a - b)
          .forEach((w) => avgMap.set(w, mean(mapW.get(w))));
        perSiembraWeekAvg.set(sid, avgMap);
      }
      return perSiembraWeekAvg;
    };

    // Construye datasets por grupo (o global) ya promediados por semana (para gráficos)
    const buildWeeklyDatasets = (paramDisplay, siembrasIds, isComparar) => {
      const field = normalizarCampo(paramDisplay);
      const perSiembraWeekAvg = weeklyAvgBySiembra(siembrasIds, field);

      const gruposTrabajo = isComparar
        ? grupos.value.filter((g) => g.ids.length).map((g) => ({ name: `Grupo ${g.gid}`, ids: g.ids }))
        : [{ name: "Promedio", ids: siembrasSeleccionadas.value }];

      // Determinar max semana global
      let maxW = 0;
      const groupWeekSeries = []; // { name, dataMap: Map(week -> avgGrupo) }
      for (const g of gruposTrabajo) {
        let gMax = 0;
        const weekToVals = new Map(); // w -> [avgSemanasDeCadaSiembraEseW]
        for (const sid of g.ids) {
          const m = perSiembraWeekAvg.get(sid);
          if (!m) continue;
          for (const [w, v] of m.entries()) {
            gMax = Math.max(gMax, w);
            const arr = weekToVals.get(w) || [];
            arr.push(v);
            weekToVals.set(w, arr);
          }
        }
        maxW = Math.max(maxW, gMax);

        // Promedio por semana (por grupo)
        const gMap = new Map();
        for (let w = 1; w <= gMax; w++) {
          const arr = weekToVals.get(w) || [];
          gMap.set(w, arr.length ? mean(arr) : null);
        }
        groupWeekSeries.push({ name: g.name, dataMap: gMap });
      }

      // Filtrado por periodo (últimas N semanas)
      let startW = 1;
      if (periodoSemanas.value !== "all") {
        const N = Number(periodoSemanas.value);
        startW = Math.max(1, maxW - N + 1);
      }

      const labels = [];
      for (let w = startW; w <= maxW; w++) labels.push(toLabel(w));

      const datasets = groupWeekSeries.map(({ name, dataMap }) => {
        const data = [];
        for (let w = startW; w <= maxW; w++) data.push(dataMap.get(w) ?? null);
        return {
          label: `${name} — ${paramDisplay}`,
          data,
          borderWidth: 2.5,
          tension: 0.25,
          spanGaps: true,
          pointRadius: 0,
          pointHoverRadius: 4,
        };
      });

      return { labels, datasets, startW, maxW, perSiembraWeekAvg, gruposTrabajo };
    };

    /** NUEVO: Estadísticos semanales por grupo (para tablas) **/
    const buildWeeklyStatsTables = (paramDisplay, siembrasIds, isComparar) => {
      const { startW, maxW, perSiembraWeekAvg, gruposTrabajo } =
        buildWeeklyDatasets(paramDisplay, siembrasIds, isComparar);

      const tables = {}; // { [groupName]: rows[] }
      for (const g of gruposTrabajo) {
        const weekToVals = new Map(); // w -> [avg por siembra]
        let gMax = 0;
        for (const sid of g.ids) {
          const m = perSiembraWeekAvg.get(sid);
          if (!m) continue;
          for (const [w, v] of m.entries()) {
            gMax = Math.max(gMax, w);
            const arr = weekToVals.get(w) || [];
            arr.push(v);
            weekToVals.set(w, arr);
          }
        }
        const thisMax = Math.max(gMax, maxW); // alinear con el global para que coincidan semanas
        const rows = [];
        for (let w = startW; w <= thisMax; w++) {
          const arr = weekToVals.get(w) || [];
          const n = arr.length;
          const m = n ? mean(arr) : null;
          const sd = n ? stdDevSample(arr) : null;
          const cv = m && sd != null && m !== 0 ? (sd / m) * 100 : null;
          const mn = n ? Math.min(...arr) : null;
          const md = n ? median(arr) : null;
          const mx = n ? Math.max(...arr) : null;
          rows.push({ week: w, n, mean: m, sd, cv, min: mn, median: md, max: mx });
        }
        tables[g.name] = rows;
      }
      return tables; // por grupo
    };

    /** Render de gráficos + cálculo de estadísticos **/
    const actualizarGraficos = async () => {
      await obtenerCalidadAgua();
      await nextTick();

      // Limpieza previa de charts
      Object.values(chartInstances.value).forEach((ch) => {
        try { ch.destroy(); } catch {}
      });
      chartInstances.value = {};
      weeklyStats.value = {};

      const seleccion = siembrasSeleccionadas.value;
      if (!seleccion.length || !parametrosSeleccionados.value.length) return;

      for (const param of parametrosSeleccionados.value) {
        // Datasets para gráficos
        const { labels, datasets } = buildWeeklyDatasets(param, seleccion, comparar.value);

        // Y padding Y
        const allVals = datasets.flatMap((d) => d.data.filter((v) => v != null));
        const hasVals = allVals.length > 0;
        const minY = hasVals ? Math.min(...allVals) : undefined;
        const maxY = hasVals ? Math.max(...allVals) : undefined;
        const pad = hasVals ? Math.max((maxY - minY) * 0.12, 1) : 0;

        // Render chart
        const el = document.getElementById(idCanvas(param));
        if (!el) continue;
        const ctx = el.getContext("2d");
        chartInstances.value[param] = new Chart(ctx, {
          type: "line",
          data: { labels, datasets },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: true } },
            interaction: { mode: "index", intersect: false },
            scales: {
              x: { title: { display: true, text: "Semana" } },
              y: {
                title: {
                  display: true,
                  text: `${param}${unidadDe(param) ? ` (${unidadDe(param)})` : ""}`,
                },
                beginAtZero: false,
                suggestedMin: hasVals ? minY - pad : undefined,
                suggestedMax: hasVals ? maxY + pad : undefined,
                ticks: { maxTicksLimit: 8 },
              },
            },
          },
        });

        // Calcular y guardar tablas de estadísticos por grupo
        weeklyStats.value[param] = buildWeeklyStatsTables(param, seleccion, comparar.value);
      }
    };

    /** PDF (solo parámetros seleccionados) + vista previa **/
    const showPreview = ref(false);
    const previewUrl = ref(null);

    const construirPDF = async ({ preview = false } = {}) => {
      await obtenerCalidadAgua();

      const doc = new jsPDF({ orientation: "portrait", unit: "pt", format: "a4" });
      const M = 44;
      const PAGE_W = doc.internal.pageSize.getWidth();
      const PAGE_H = doc.internal.pageSize.getHeight();
      const CONTENT_W = PAGE_W - M * 2;
      const setFont = (f = "helvetica", s = 9, st = "normal") => {
        doc.setFont(f, st);
        doc.setFontSize(s);
      };

      // Encabezado
      setFont("helvetica", 16, "bold");
      doc.text("Reporte de Calidad de Agua (Agregación semanal)", M, M + 6);
      setFont("helvetica", 9);
      doc.setTextColor(120);
      doc.text(`Generado: ${formatDate(new Date())}`, PAGE_W - M, M + 6, { align: "right" });
      doc.setTextColor(0);
      doc.setDrawColor(230);
      doc.line(M, M + 12, PAGE_W - M, M + 12);

      let y = M + 28;

      // Resumen
      const paramResumen = parametrosSeleccionados.value.join(", ");
      const resumenL = [
        `Parámetro(s): ${paramResumen}`,
        `Periodo: ${
          periodoSemanas.value === "all" ? "Completo" : `Últimas ${String(periodoSemanas.value)} semanas`
        }`,
        `Alineación: Semanas desde el primer registro de cada siembra`,
        comparar.value
          ? `Comparación: ${grupos.value.filter((g) => g.ids.length).map((g) => `G${g.gid}(${g.ids.length})`).join(" vs ")}`
          : `Promedio global de ${String(siembrasSeleccionadas.value.length)} siembra(s)`,
      ];

      setFont("helvetica", 11, "bold");
      doc.text("Resumen", M, y);
      y += 14;
      setFont("helvetica", 9);
      resumenL.forEach((line) => {
        doc.text(doc.splitTextToSize(String(line), CONTENT_W), M, y);
        y += 12;
      });
      y += 4;

      // Tabla de siembras / grupos
      const putGroupTable = (title, rows) => {
        setFont("helvetica", 10, "bold");
        if (y + 26 > PAGE_H - M) {
          doc.addPage();
          y = M;
        }
        doc.text(String(title), M, y);
        y += 6;
        autoTable(doc, {
          startY: y + 8,
          margin: { left: M, right: M },
          styles: { font: "helvetica", fontSize: 9, cellPadding: 5, overflow: "linebreak" },
          headStyles: { fillColor: [40, 167, 69], textColor: 255, halign: "center" },
          bodyStyles: { halign: "center" },
          columnStyles: {
            0: { cellWidth: CONTENT_W * 0.30 }, // Estanque
            1: { cellWidth: CONTENT_W * 0.18 }, // Inicio
            2: { cellWidth: CONTENT_W * 0.18 }, // Fin
            3: { cellWidth: CONTENT_W * 0.16 }, // Especie
            4: { cellWidth: CONTENT_W * 0.18 }, // Parámetros
          },
          head: [["Estanque", "Inicio", "Fin", "Especie", "Parámetros"]],
          body: rows,
        });
        y = doc.lastAutoTable.finalY + 12;
      };

      if (comparar.value) {
        grupos.value.forEach((g) => {
          if (!g.ids.length) return;
          const rows = g.ids.map((id) => {
            const s = siembraPorId.value.get(id);
            const estanque = nombreEstanquePorId.value.get(s.estanque) || s.estanque;
            const inicio = firstDatoFecha(id);
            const fin = lastDatoFecha(id);
            return [String(estanque), String(inicio), String(fin), String(s.especie), String(paramResumen)];
          });
          putGroupTable(`Grupo ${g.gid}`, rows);
        });
      } else {
        const rows = siembrasSeleccionadas.value.map((id) => {
          const s = siembraPorId.value.get(id);
          const estanque = nombreEstanquePorId.value.get(s.estanque) || s.estanque;
          const inicio = firstDatoFecha(id);
          const fin = lastDatoFecha(id);
          return [String(estanque), String(inicio), String(fin), String(s.especie), String(paramResumen)];
        });
        putGroupTable("Siembras", rows);
      }

      // Helpers PDF
      const CHART_H = 240;
      const addChart = (title, canvasId) => {
        setFont("helvetica", 10, "bold");
        if (y + CHART_H + 28 > PAGE_H - M) {
          doc.addPage();
          y = M;
        }
        doc.text(String(title), M, y);
        y += 10;
        const canvas = document.getElementById(canvasId);
        if (canvas) {
          const imgData = canvas.toDataURL("image/png", 1.0);
          doc.addImage(imgData, "PNG", M, y, CONTENT_W, CHART_H, "", "FAST");
          y += CHART_H + 12;
        }
      };

      const addStatsTablesForParam = (param) => {
        // Asegurar que tengamos stats (recalcular si fuera necesario)
        if (!weeklyStats.value[param]) {
          weeklyStats.value[param] = buildWeeklyStatsTables(param, siembrasSeleccionadas.value, comparar.value);
        }
        const groupsTables = weeklyStats.value[param];

        for (const [gname, rows] of Object.entries(groupsTables)) {
          setFont("helvetica", 10, "bold");
          if (y + 26 > PAGE_H - M) {
            doc.addPage();
            y = M;
          }
          doc.text(`Estadísticos — ${gname} — ${param}${unidadDe(param)?` (${unidadDe(param)})`:''}`, M, y);
          y += 6;

          // Cuerpo de la tabla
          const body = rows.map((r) => [
            `Semana ${r.week}`,
            String(r.n),
            fmt(r.mean),
            fmt(r.sd),
            fmt(r.cv),
            fmt(r.min),
            fmt(r.median),
            fmt(r.max),
          ]);

          autoTable(doc, {
            startY: y + 8,
            margin: { left: M, right: M },
            styles: { font: "helvetica", fontSize: 9, cellPadding: 4, overflow: "linebreak" },
            headStyles: { fillColor: [240, 240, 240], textColor: 20, halign: "center" },
            bodyStyles: { halign: "center" },
            head: [["Semana", "n", "Promedio", "Desv. Est.", "CV%", "Mín", "Mediana", "Máx"]],
            body,
          });
          y = doc.lastAutoTable.finalY + 12;
        }
      };

      // Por parámetro: gráfico y luego tablas de estadísticos por grupo
      for (const param of parametrosSeleccionados.value) {
        addChart(`${param}${unidadDe(param) ? ` (${unidadDe(param)})` : ""}`, idCanvas(param));
        addStatsTablesForParam(param);
      }

      // Pie de página (numeración)
      const pageCount = doc.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        setFont("helvetica", 9);
        doc.setTextColor(120);
        doc.text(`Página ${i} de ${pageCount}`, PAGE_W / 2, PAGE_H - 12, { align: "center" });
        doc.setTextColor(0);
      }

      if (preview) {
        const blob = doc.output("blob");
        if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
        const url = URL.createObjectURL(blob);
        return url;
      } else {
        doc.save(`reporte_calidad_agua_${Date.now()}.pdf`);
        return null;
      }
    };

    const mostrarVistaPrevia = async () => {
      const url = await construirPDF({ preview: true });
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
    const exportarReporte = async () => {
      await construirPDF({ preview: false });
    };

    /** Init **/
    onMounted(async () => {
      await Promise.all([obtenerEstanques(), obtenerTodasLasSiembras(), obtenerCalidadAgua()]);
    });

    return {
      // datos base
      estanques, todasSiembras, datos,

      // selección
      siembrasSeleccionadas, expandido, busquedaEstanque, busquedaSiembra,

      // grupos
      GRUPO_MAX, comparar, asignacionGrupo, grupos, hayGruposConMiembros,
      grupoDeSiembra, toggleGrupo, removerDeGrupo, vaciarGrupo,

      // filtros/acciones
      estanquesFiltrados, siembrasDeEstanqueFiltradas, conteoSiembras,
      toggleExpand, seleccionarTodasDeEstanque, limpiarDeEstanque,
      seleccionarTodasVisibles, limpiarSeleccion, quitarSiembra,

      // parámetros/periodos
      parametrosActuales, parametrosSeleccionados, periodoSemanas, periodosSemanas, unidadDe,

      // charts y stats
      chartInstances, tituloSerie, idCanvas, toLabel, fmt,
      actualizarGraficos, weeklyStats,

      // pdf preview
      showPreview, previewUrl, mostrarVistaPrevia, exportarReporte, cerrarPreview,

      // etiquetas
      etiquetaSiembra, etiquetaSiembraPorId, nickSiembra,
    };
  },
};
</script>

<style scoped>
/* Base */
.grafico-container {
  font-family: 'Poppins', sans-serif;
  max-width: auto;
  margin: 30px auto;
  padding: 25px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}

.form-seleccion { margin-bottom: 20px; }
.form-group { margin-bottom: 16px; display: flex; flex-direction: column; }
label { font-weight: 600; margin-bottom: 8px; color: #444; font-size: 14px; }

select, .input {
  width: 100%; padding: 12px;
  border: 1px solid #ddd; border-radius: 8px;
  font-size: 14px; background: #f8f9fa;
  transition: all .2s ease-in-out;
}
.input.small { padding: 8px 10px; font-size: 13px; }
select:focus, .input:focus { border-color: #28a745; outline: none; box-shadow: 0 0 5px rgba(40,167,69,.35); }

/* Bloques una columna */
.one-col .block { margin-bottom: 16px; }
.card { border: 1px solid #eee; border-radius: 12px; padding: 12px; }
.card.inner { margin-top: 12px; }
.block-title { margin-bottom: 8px; display: block; }

.toolbar-top {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  padding: 12px;
  margin-bottom: 12px;
  border: 1px solid #eee;
  border-radius: 12px;
  background: #fbfffc;
}


/* Lista de estanques/siembras */
.list { list-style: none; margin: 0; padding: 0; }
.ponds { margin-top: 10px; }
.pond-row { border: 1px solid #eee; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
.pond-row-main { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 6px 4px; border-radius: 8px; }
.pond-row-main.clickable { cursor: pointer; }
.pond-row-main.clickable:hover { background: #f8fff9; }
.checkbox-label { display: inline-flex; align-items: center; gap: 8px; cursor: pointer; }
.pond-name { font-weight: 600; }
.pond-meta { display: flex; align-items: center; gap: 10px; }
.meta { color: #666; }
.chev { color: #28a745; font-weight: 700; }

.siembras-panel { margin-top: 10px; padding-top: 10px; border-top: 1px dashed #e5e5e5; }
.panel-actions { display: flex; gap: 8px; margin-bottom: 8px; }

.siembras-list { list-style: none; margin: 8px 0 0; padding: 0; max-height: 260px; overflow: auto; }
.siembras-list li { padding: 6px 0; border-bottom: 1px dashed #f0f0f0; display: flex; align-items: center; justify-content: space-between; gap: 10px; }

/* Botones de grupos */
.grp-buttons { display: inline-flex; gap: 4px; flex-wrap: wrap; }
.grp-btn { border: 1px solid #cfd; border-radius: 6px; padding: 4px 6px; font-size: 12px; cursor: pointer; background: #fff; min-width: 28px; text-align: center; }
.grp-btn.active { background: #eaffef; border-color: #28a745; font-weight: 700; }

/* Chips */
.chips { display: flex; gap: 8px; flex-wrap: wrap; margin: 6px 0 10px; }
.chip { background: #f0fff4; border: 1px solid #d1f5dc; color: #1d7f3b; padding: 6px 10px; border-radius: 999px; font-size: 12px; display: inline-flex; gap: 6px; align-items: center; }
.chip.tiny { font-size: 11px; padding: 4px 8px; }
.chip-x { background: transparent; border: none; cursor: pointer; font-size: 14px; line-height: 1; color: #1d7f3b; }

.quick-actions { display: flex; gap: 8px; margin: 8px 0 4px; flex-wrap: wrap; }
.toggle { display: flex; gap: 8px; align-items: center; cursor: pointer; }
.toggle input { transform: scale(1.1); }

/* Parámetros */
.param-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(180px,1fr)); gap: 8px; }

/* Chart: responsive y alto */
.chart-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
.chart-wrap { position: relative; width: 100%; height: clamp(460px, 70vh, 880px); }
canvas { margin-top: 0; max-width: 100%; }
.grafico-individual { margin-bottom: 30px; }

/* Tablas de estadísticos */
.stats-wrap { margin-top: 12px; }
.stats-title { margin: 8px 0; }
.stats-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.stats-table th, .stats-table td {
  padding: 8px; border: 1px solid #ddd; text-align: center;
}
.stats-table thead th {
  background: #f8f9fa; font-weight: 700;
}

/* Botones */
button { transition: transform .1s ease-in-out; }
button:hover { transform: scale(1.02); }
button:active { transform: scale(0.98); }
.btn-cta { background: #28a745; color: #fff; border: none; padding: 12px 15px; border-radius: 8px; font-weight: 700; }
.btn-generar { margin-top: 12px; background: #28a745; color: #fff; border: none; padding: 12px 15px; border-radius: 8px; font-weight: 700; }
.btn-generar.outline { background:#fff; color:#28a745; border:1px solid #28a745; }

/* Botonera PDF */
.btn-row { display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px; }

/* Transición acordeones */
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.hint { color: #666; font-size: 12px; }
.grupo-line { display:flex; align-items:center; gap:8px; flex-wrap: wrap; margin: 6px 0; }

/* Modal preview */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.35); display: flex; align-items: center; justify-content: center; z-index: 9999; }
.modal { width: min(1000px, 92vw); height: min(85vh, 900px); background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,.2); display: flex; flex-direction: column; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-bottom: 1px solid #eee; }
.pdf-frame { width: 100%; height: 100%; border: 0; }
</style>
