<template>
  <div class="grafico-container">
    <h1>Visualización de Crecimiento por Estanque (mezcla de siembras)</h1>

    <form class="form-seleccion one-col" @submit.prevent="actualizarGrafico">
      <!-- OPCIONES RÁPIDAS (al inicio): Alinear / Comparar -->
      <div class="card block">
        <div class="form-group toggles">
          <label class="toggle">
            <input type="checkbox" v-model="alinearSemanas" />
            <span>Alinear por semanas (desde la fecha de siembra)</span>
          </label>
          <label class="toggle">
            <input type="checkbox" v-model="comparar" />
            <span>Comparar Siembras (hasta {{ GRUPO_MAX }} grupos)</span>
          </label>
        </div>
        <small class="hint" v-if="comparar">
          Activa “Comparar” y asigna cada siembra a un grupo (botones 1..10 junto a cada siembra).
          El gráfico mostrará una línea por grupo con el promedio de sus siembras.
        </small>
      </div>

      <!-- Estanques + Siembras -->
      <div class="card block">
        <label class="block-title">Estanques y Siembras</label>
        <input
          v-model="busquedaEstanque"
          type="text"
          class="input"
          placeholder="Buscar estanque por nombre…"
        />

        <ul class="list ponds">
          <li v-for="e in estanquesFiltrados" :key="e.id_estanque" class="pond-row">
            <!-- Click en toda la barra para expandir -->
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
                  <button type="button" class="btn-sm" @click="seleccionarTodasDeEstanque(e.id_estanque)">
                    Seleccionar todas
                  </button>
                  <button type="button" class="btn-sm outline" @click="limpiarDeEstanque(e.id_estanque)">
                    Limpiar
                  </button>
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
                      <input
                        type="checkbox"
                        :value="s.id_siembra"
                        v-model="siembrasSeleccionadas"
                      />
                      <span>{{ etiquetaSiembra(s) }}</span>
                    </label>

                    <!-- Asignación a grupos (1..10) si comparar -->
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
      </div>

      <!-- Resumen de selección + acciones rápidas -->
      <div class="card block">
        <label class="block-title">Siembras seleccionadas</label>

        <div class="chips" v-if="siembrasSeleccionadas.length">
          <span class="chip" v-for="sid in siembrasSeleccionadas" :key="sid">
            {{ etiquetaSiembraPorId(sid) }}
            <button type="button" class="chip-x" @click="quitarSiembra(sid)">×</button>
          </span>
        </div>
        <div class="muted" v-else>Sin siembras seleccionadas.</div>

        <div class="quick-actions">
          <button type="button" class="btn-sm" @click="seleccionarTodasVisibles">
            Seleccionar todas las visibles
          </button>
          <button type="button" class="btn-sm outline" @click="limpiarSeleccion">
            Limpiar selección
          </button>
        </div>

        <!-- Resumen de grupos -->
        <div v-if="comparar" class="grupos-summary">
          <div
            v-for="g in grupos"
            :key="g.gid"
            class="grupo-line"
            v-show="g.ids.length"
          >
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

      <!-- Periodo y Rubro -->
      <div class="card block">
        <div class="form-group">
          <label for="periodo">Periodo</label>
          <select v-model="periodoSeleccionado" required>
            <option v-for="p in periodos" :key="p" :value="p">{{ p }}</option>
          </select>
          <small class="hint" v-if="periodoSeleccionado==='Completo'">
            Completo = desde la primera medición de las siembras seleccionadas hasta la más reciente.
          </small>
        </div>

        <div class="form-group">
          <label for="parametro">Rubro</label>
          <select v-model="parametroSeleccionado" required>
            <option value="Todos los rubros">Todos los rubros</option>
            <option v-for="r in parametrosActuales" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>

        <button
          type="submit"
          :disabled="siembrasSeleccionadas.length === 0 || (comparar && !hayGruposConMiembros)"
          class="btn-cta"
          title="Generar gráfico"
        >
          Generar Gráfico(s)
        </button>
      </div>
    </form>

    <!-- GRÁFICO GLOBAL -->
    <div class="grafico-individual">
      <div class="chart-header">
        <h3>
          {{ parametroSeleccionado }}
          <span v-if="siembrasSeleccionadas.length"> — {{ tituloSerie }}</span>
        </h3>
      </div>
      <div class="chart-wrap">
        <canvas id="grafico"></canvas>
      </div>
    </div>

    <!-- TABLAS DE DISTRIBUCIÓN -->
    <div v-if="!comparar">
      <div v-for="(segmentos, fecha) in distribucionTallas" :key="fecha" class="grafico-individual">
        <h3>Distribución de Tallas - {{ fecha }}</h3>
        <table>
          <thead>
            <tr><th>Rango (gr)</th><th>Cantidad</th></tr>
          </thead>
          <tbody>
            <tr v-for="segmento in segmentos" :key="segmento.etiqueta">
              <td>{{ segmento.etiqueta }}</td>
              <td>{{ segmento.cantidad }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modo comparar: distribución por grupo y por fecha -->
    <div v-else>
      <div
        v-for="(mapaFechas, nombreGrupo) in distribucionTallasGrupos"
        :key="nombreGrupo"
        class="grafico-individual"
      >
        <h3>Distribución de Tallas — {{ nombreGrupo }}</h3>

        <div v-for="(segmentos, fecha) in mapaFechas" :key="nombreGrupo + '_' + fecha" class="grafico-individual">
          <h4>{{ fecha }}</h4>
          <table>
            <thead>
              <tr><th>Rango (gr)</th><th>Cantidad</th></tr>
            </thead>
            <tbody>
              <tr v-for="segmento in segmentos" :key="segmento.etiqueta">
                <td>{{ segmento.etiqueta }}</td>
                <td>{{ segmento.cantidad }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Botones PDF -->
    <div class="btn-row">
      <button type="button" class="btn-generar outline" @click="mostrarVistaPrevia">Vista previa PDF</button>
      <button type="button" class="btn-generar" @click="exportarReporte">Descargar PDF</button>
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
import { ref, onMounted, watch, computed, nextTick } from "vue";
import axios from "@/services/axios";
import Chart from "chart.js/auto";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

 // util local
    
    const readFarmNameFromStorage = () => {
      try {
        const user = JSON.parse(localStorage.getItem("user") || "{}");
        const raw =
          user.acuicolaNombre ??
          user.acuicola_name ??
          user.acuicola ??
          user.empresa ??
          "Granja Acuícola";
        return String(raw); // <-- fuerza string
      } catch {
        return "Granja Acuícola";
      }
    };

export default {
  name: "Crecimiento",
  setup() {
    // Datos base
    const estanques = ref([]);
    const todasSiembras = ref([]);
    const datos = ref([]);
    const rubros = ref([]);
    const farmName = ref(readFarmNameFromStorage());

    // Selección
    const siembrasSeleccionadas = ref([]);

    // Comparar: hasta 10 grupos
    const GRUPO_MAX = 10;
    const comparar = ref(false);
    const asignacionGrupo = ref({}); // { [siembraId]: number 1..10 }

    const grupos = computed(() => {
      const base = new Map(Array.from({ length: GRUPO_MAX }, (_, i) => [i + 1, []]));
      siembrasSeleccionadas.value.forEach(id => {
        const g = asignacionGrupo.value[id];
        if (g && base.has(g)) base.get(g).push(id);
      });
      return Array.from(base, ([gid, ids]) => ({ gid, ids }));
    });
    const hayGruposConMiembros = computed(() => grupos.value.some(g => g.ids.length > 0));

    // Buscadores y UI
    const busquedaEstanque = ref("");
    const busquedaSiembra = ref({}); // estanqueId -> texto
    const expandido = ref({});       // estanqueId -> bool

    // Parámetros/rangos
    const parametrosActuales = ref([]);
    const distribucionTallas = ref({});
    const distribucionTallasGrupos = ref({}); // { "Grupo 1": { "2025-07-01": [...], ... }, ... }
    const chartInstances = ref({});

    const parametroSeleccionado = ref("Todos los rubros");
    const periodoSeleccionado = ref("Completo");
    const alinearSemanas = ref(true); // ON por defecto

    // Vista previa PDF
    const showPreview = ref(false);
    const previewUrl = ref(null);

    // Mapas rubro <-> etiqueta
    const etiquetaPorIdRubro = ref(new Map());
    const idRubroPorEtiqueta = ref(new Map());

    // Periodos en dropdown (incluye "Completo")
    const diasPorPeriodo = {
      "Hoy": 1, "7 días": 7, "15 días": 15, "1 mes": 30,
      "2 meses": 60, "3 meses": 90, "4 meses": 120, "5 meses": 150,
      "6 meses": 180, "7 meses": 210,
    };
    const periodos = computed(() => ["Completo", ...Object.keys(diasPorPeriodo)]);

    const formatDate = (fecha) => new Date(fecha).toISOString().split("T")[0];

    
    // Carga inicial
    const obtenerEstanques = async () => {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      farmName.value = readFarmNameFromStorage(); // <-- string garantizado

      const res = await axios.get("/estanque/");
      estanques.value = res.data.filter(e => e.estatus && (!user || e.acuicola === user.acuicola));
    };
    const obtenerTodasLasSiembras = async () => {
      const res = await axios.get("/siembra/");
      todasSiembras.value = res.data;
    };

    // Helpers siembras
    const nombreEstanquePorId = computed(() => {
      const m = new Map();
      estanques.value.forEach(e => m.set(e.id_estanque, e.nombre));
      return m;
    });

    const etiquetaSiembra = (s) => {
      const estName = nombreEstanquePorId.value.get(s.estanque) || `Estanque ${s.estanque}`;
      return `${formatDate(s.fecha)} — ${s.especie} — ${estName}`;
    };

    const siembraPorId = computed(() => {
      const m = new Map();
      todasSiembras.value.forEach(s => m.set(s.id_siembra, s));
      return m;
    });

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

    const lastDatoFecha = (siembraId) => {
      const arr = datos.value.filter(d => d.siembra === siembraId);
      if (!arr.length) return "–";
      const maxT = Math.max(...arr.map(d => new Date(d.fecha).getTime()));
      return formatDate(new Date(maxT));
    };

    const firstDatoFecha = (siembraId) => {
      const arr = datos.value.filter(d => d.siembra === siembraId);
      if (!arr.length) return "–";
      const minT = Math.min(...arr.map(d => new Date(d.fecha).getTime()));
      return formatDate(new Date(minT));
    };

    // Filtros UI
    const estanquesFiltrados = computed(() => {
      const q = busquedaEstanque.value.trim().toLowerCase();
      if (!q) return estanques.value;
      return estanques.value.filter(e => (e.nombre || "").toLowerCase().includes(q));
    });

    const siembrasDeEstanque = (estanqueId) =>
      todasSiembras.value.filter(s => s.estanque === estanqueId);

    const siembrasDeEstanqueFiltradas = (estanqueId) => {
      const q = (busquedaSiembra.value[estanqueId] || "").trim().toLowerCase();
      let arr = siembrasDeEstanque(estanqueId);
      if (!q) return arr;
      return arr.filter(s => etiquetaSiembra(s).toLowerCase().includes(q));
    };

    const conteoSiembras = (estanqueId) => siembrasDeEstanque(estanqueId).length;

    // Acciones UI
    const toggleExpand = (estanqueId) => {
      expandido.value[estanqueId] = !expandido.value[estanqueId];
    };

    const seleccionarTodasDeEstanque = (estanqueId) => {
      const ids = siembrasDeEstanqueFiltradas(estanqueId).map(s => s.id_siembra);
      const set = new Set([...siembrasSeleccionadas.value, ...ids]);
      siembrasSeleccionadas.value = Array.from(set);
    };

    const limpiarDeEstanque = (estanqueId) => {
      const ids = new Set(siembrasDeEstanque(estanqueId).map(s => s.id_siembra));
      siembrasSeleccionadas.value = siembrasSeleccionadas.value.filter(id => !ids.has(id));
      // limpiar grupos para esos ids
      ids.forEach(id => { delete asignacionGrupo.value[id]; });
    };

    const seleccionarTodasVisibles = () => {
      const visibles = [];
      for (const e of estanquesFiltrados.value) {
        visibles.push(...siembrasDeEstanqueFiltradas(e.id_estanque).map(s => s.id_siembra));
      }
      const set = new Set([...siembrasSeleccionadas.value, ...visibles]);
      siembrasSeleccionadas.value = Array.from(set);
    };

    const limpiarSeleccion = () => {
      siembrasSeleccionadas.value = [];
      asignacionGrupo.value = {};
    };

    const quitarSiembra = (sid) => {
      siembrasSeleccionadas.value = siembrasSeleccionadas.value.filter(x => x !== sid);
      delete asignacionGrupo.value[sid];
    };

    const grupoDeSiembra = (sid) => asignacionGrupo.value[sid] || null;

    const toggleGrupo = (sid, grupo) => {
      if (!siembrasSeleccionadas.value.includes(sid)) {
        siembrasSeleccionadas.value = [...siembrasSeleccionadas.value, sid];
      }
      if (asignacionGrupo.value[sid] === grupo) {
        delete asignacionGrupo.value[sid];
      } else {
        asignacionGrupo.value[sid] = grupo;
      }
    };

    const removerDeGrupo = (sid) => { delete asignacionGrupo.value[sid]; };
    const vaciarGrupo = (grupo) => {
      Object.keys(asignacionGrupo.value).forEach(k => {
        if (asignacionGrupo.value[k] === grupo) delete asignacionGrupo.value[k];
      });
    };

    // Rubros según siembras elegidas
    const obtenerRubros = async () => {
      if (siembrasSeleccionadas.value.length === 0) {
        parametrosActuales.value = [];
        etiquetaPorIdRubro.value = new Map();
        idRubroPorEtiqueta.value = new Map();
        return;
      }

      const [crecimientos, rubrosData] = await Promise.all([
        axios.get("/crecimiento/"),
        axios.get("/rubro/")
      ]);
      rubros.value = rubrosData.data;

      const usados = crecimientos.data.filter(c => siembrasSeleccionadas.value.includes(c.siembra));
      const idsUnicos = [...new Set(usados.map(c => c.rubro))];

      const ePorId = new Map();
      const idPorE = new Map();
      const opciones = [];

      idsUnicos.forEach(id => {
        const r = rubros.value.find(x => x.id_rubro === id);
        if (!r) return;
        const etiqueta = `${r.nombre} (${r.unidad})`;
        ePorId.set(id, etiqueta);
        idPorE.set(etiqueta, id);
        opciones.push(etiqueta);
      });

      etiquetaPorIdRubro.value = ePorId;
      idRubroPorEtiqueta.value = idPorE;
      parametrosActuales.value = opciones;

      if (parametroSeleccionado.value !== "Todos los rubros" &&
          !idRubroPorEtiqueta.value.has(parametroSeleccionado.value)) {
        parametroSeleccionado.value = "Todos los rubros";
      }
    };

    const obtenerDatos = async () => {
      if (siembrasSeleccionadas.value.length === 0) {
        datos.value = [];
        return;
      }
      const res = await axios.get("/crecimiento/");
      datos.value = res.data.filter(d => siembrasSeleccionadas.value.includes(d.siembra));
    };

    const calcularRangoCompleto = (lista) => {
      if (!lista || lista.length === 0) return null;
      const t = lista.map(d => new Date(d.fecha).getTime());
      const minT = Math.min(...t);
      const maxT = Math.max(...t);
      return { inicio: new Date(minT), fin: new Date(maxT) };
    };

    const tituloSerie = computed(() => {
      if (!comparar.value) return `Promedio de ${siembrasSeleccionadas.value.length} siembra(s)`;
      const gruposConCount = grupos.value.filter(g => g.ids.length).map(g => `G${g.gid}(${g.ids.length})`);
      return `Comparación ${gruposConCount.join(" · ")}`;
    });

    // Agregación por FECHA CALENDARIO
    const seriesPorFecha = (datosRango, rubroId, siembrasIds) => {
      const setFechas = new Set(datosRango.map(r => formatDate(r.fecha)));
      const etiquetasOrdenadas = Array.from(setFechas).sort((a,b)=> new Date(a)-new Date(b));

      const serie = etiquetasOrdenadas.map(f => {
        const proms = siembrasIds.map(idS => {
          const vals = datosRango
            .filter(d => d.siembra===idS && d.rubro===rubroId && formatDate(d.fecha)===f)
            .map(d => d.medicion);
          if (!vals.length) return null;
          return vals.reduce((a,b)=>a+b,0)/vals.length;
        }).filter(v=>v!==null);
        return proms.length ? (proms.reduce((a,b)=>a+b,0)/proms.length) : null;
      });

      return { etiquetas: etiquetasOrdenadas, serie };
    };

    // Agregación por SEMANAS desde la fecha de siembra (robusta)
    const seriesPorSemana = (datosRango, rubroId, siembrasIds) => {
      const MSW = 7 * 24 * 60 * 60 * 1000;

      // inicios válidos
      const starts = new Map();
      siembrasIds.forEach(id => {
        const raw = siembraPorId.value.get(id)?.fecha;
        const ts = Date.parse(raw);
        if (!Number.isNaN(ts)) starts.set(id, ts);
      });
      if (starts.size === 0) return { etiquetas: [], serie: [] };

      // (siembra|semana) -> [valores]
      const mapSW = new Map();
      for (const d of datosRango) {
        if (d.rubro !== rubroId) continue;
        const startTs = starts.get(d.siembra);
        if (startTs == null) continue;

        const ts = Date.parse(d.fecha);
        if (Number.isNaN(ts)) continue;

        const w = Math.floor((ts - startTs) / MSW) + 1;
        if (!Number.isFinite(w) || w < 1) continue;

        const key = `${d.siembra}|${w}`;
        const arr = mapSW.get(key) || [];
        arr.push(d.medicion);
        mapSW.set(key, arr);
      }

      let maxW = 0;
      for (const key of mapSW.keys()) {
        const w = parseInt(key.split("|")[1], 10);
        if (Number.isFinite(w) && w > maxW) maxW = w;
      }
      if (maxW === 0) return { etiquetas: [], serie: [] };

      const etiquetas = Array.from({ length: maxW }, (_, i) => `Semana ${i + 1}`);
      const serie = etiquetas.map((_, idx) => {
        const w = idx + 1;
        const proms = [];
        for (const idS of siembrasIds) {
          const vals = mapSW.get(`${idS}|${w}`) || [];
          if (vals.length) proms.push(vals.reduce((a, b) => a + b, 0) / vals.length);
        }
        return proms.length ? proms.reduce((a, b) => a + b, 0) / proms.length : null;
      });

      return { etiquetas, serie };
    };

    // Construcción del gráfico
    const actualizarGrafico = async () => {
      await obtenerDatos();
      await nextTick();

      // 1) Rango temporal
      let inicio, fin;
      if (periodoSeleccionado.value === "Completo") {
        const rango = calcularRangoCompleto(datos.value);
        if (!rango) {
          if (chartInstances.value.individual) chartInstances.value.individual.destroy();
          distribucionTallas.value = {};
          distribucionTallasGrupos.value = {};
          return;
        }
        inicio = rango.inicio; fin = rango.fin;
      } else {
        const dias = diasPorPeriodo[periodoSeleccionado.value];
        fin = new Date();
        inicio = new Date(); inicio.setDate(fin.getDate() - (dias - 1));
      }

      // 2) Filtrar por rango calendario (distribuciones y modo fecha)
      const datosRango = datos.value.filter(d => {
        const f = new Date(d.fecha);
        return f >= inicio && f <= fin;
      });

      // 3) Rubros a graficar
      const rubrosSeleccionados = (parametroSeleccionado.value === "Todos los rubros")
        ? parametrosActuales.value
        : [parametroSeleccionado.value];

      // 4) Armar datasets
      const buildDataset = (etiquetaRubro, ids, prefix="") => {
        const rubroId = idRubroPorEtiqueta.value.get(etiquetaRubro);
        const agg = alinearSemanas.value
          ? seriesPorSemana(datosRango, rubroId, ids)
          : seriesPorFecha(datosRango, rubroId, ids);
        return {
          etiquetas: agg.etiquetas,
          dataset: {
            label: prefix ? `${prefix} — ${etiquetaRubro}` : etiquetaRubro,
            data: agg.serie,
            borderWidth: 2.5,
            tension: 0.25,
            spanGaps: true,
            pointRadius: 0,
            pointHoverRadius: 4
          }
        };
      };

      let etiquetasEjeX = [];
      const datasets = [];

      if (comparar.value) {
        grupos.value.forEach(g => {
          if (!g.ids.length) return;
          rubrosSeleccionados.forEach(r => {
            const { etiquetas, dataset } = buildDataset(r, g.ids, `Grupo ${g.gid}`);
            if (etiquetas.length > etiquetasEjeX.length) etiquetasEjeX = etiquetas;
            datasets.push(dataset);
          });
        });
      } else {
        rubrosSeleccionados.forEach(r => {
          const { etiquetas, dataset } = buildDataset(r, siembrasSeleccionadas.value);
          if (etiquetas.length > etiquetasEjeX.length) etiquetasEjeX = etiquetas;
          datasets.push(dataset);
        });
      }

      // 5) Destruir y crear gráfico
      if (chartInstances.value.individual) {
        chartInstances.value.individual.destroy();
      }

      const ctx = document.getElementById("grafico").getContext("2d");

      // Y dinámico con padding
      const allVals = datasets.flatMap(d => d.data.filter(v => v != null));
      const hasVals = allVals.length > 0;
      const minY = hasVals ? Math.min(...allVals) : undefined;
      const maxY = hasVals ? Math.max(...allVals) : undefined;
      const pad = hasVals ? Math.max((maxY - minY) * 0.12, 1) : 0;

      chartInstances.value.individual = new Chart(ctx, {
        type: "line",
        data: { labels: etiquetasEjeX, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true } },
          interaction: { mode: 'index', intersect: false },
          scales: {
            x: {
              title: { display: true, text: alinearSemanas.value ? "Semana" : "Fecha" },
              ticks: { maxRotation: alinearSemanas.value ? 0 : 90, minRotation: alinearSemanas.value ? 0 : 90 }
            },
            y: {
              title: { display: true, text: "Medición promedio" },
              beginAtZero: false,
              suggestedMin: hasVals ? (minY - pad) : undefined,
              suggestedMax: hasVals ? (maxY + pad) : undefined,
              ticks: { maxTicksLimit: 8 }
            }
          }
        }
      });

      // 6) Distribución (por fecha calendario del rango)
      distribucionTallas.value = {};
      distribucionTallasGrupos.value = {};

      const construirMapaDistribucion = (filtrados) => {
        const mapa = {};
        filtrados.forEach(d => {
          const fecha = formatDate(d.fecha);
          if (!mapa[fecha]) mapa[fecha] = [];
          mapa[fecha].push(d.medicion);
        });

        const resultado = {};
        for (const [fecha, mediciones] of Object.entries(mapa)) {
          if (!mediciones.length) continue;
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
          resultado[fecha] = segmentos;
        }
        return resultado;
      };

      if (comparar.value) {
        grupos.value.forEach(g => {
          if (!g.ids.length) return;
          const filtrados = datosRango.filter(d => g.ids.includes(d.siembra));
          const mapa = construirMapaDistribucion(filtrados);
          if (Object.keys(mapa).length) {
            distribucionTallasGrupos.value[`Grupo ${g.gid}`] = mapa;
          }
        });
      } else {
        const mapa = construirMapaDistribucion(datosRango);
        distribucionTallas.value = mapa;
      }
    };

    // ====== PDF profesional + preview ======
    const construirPDF = async ({ preview = false } = {}) => {
      await obtenerDatos();

      // Config base A4 en puntos
      const doc = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' });
      const M = 44; // márgenes
      const PAGE_W = doc.internal.pageSize.getWidth();
      const PAGE_H = doc.internal.pageSize.getHeight();
      const CONTENT_W = PAGE_W - M * 2;

      const setFont = (f='helvetica', s=9, st='normal') => {
        doc.setFont(f, st);
        doc.setFontSize(s);
      };

      // ====== Encabezado institucional (repetido en todas las páginas al final) ======
      const drawHeader = (p) => {
    doc.setPage(p);
    setFont('helvetica', 11, 'bold');
    const title = String(farmName.value || 'Granja Acuícola'); // <-- fuerza string
    doc.text(title, PAGE_W / 2, M - 14, { align: 'center' });
    doc.setDrawColor(230);
    doc.line(M, M - 10, PAGE_W - M, M - 10);
  };

      // ====== Portada / Encabezado de contenido (página 1) ======
      const ahora = new Date();
      const fechaStr = `${ahora.getFullYear()}-${String(ahora.getMonth()+1).padStart(2,'0')}-${String(ahora.getDate()).padStart(2,'0')}`;

      setFont('helvetica', 16, 'bold');
      doc.text('Reporte de Crecimiento (mezcla de siembras)', M, M + 6);

      setFont('helvetica', 9);
      doc.setTextColor(120);
      doc.text(`Generado: ${fechaStr}`, PAGE_W - M, M + 6, { align: 'right' });
      doc.setTextColor(0);

      doc.setDrawColor(230); doc.line(M, M + 12, PAGE_W - M, M + 12);

      let y = M + 28;

      // ====== Resumen general ======
      // Periodo (resuelve "Completo" a fechas)
      let periodoTexto = periodoSeleccionado.value;
      if (periodoSeleccionado.value === 'Completo' && datos.value.length) {
        const rango = calcularRangoCompleto(datos.value);
        if (rango) periodoTexto = `Completo (${formatDate(rango.inicio)} a ${formatDate(rango.fin)})`;
      }

      setFont('helvetica', 11, 'bold'); doc.text('Resumen', M, y); y += 14;
      setFont('helvetica', 9);
      const resumenL = [
        `Rubro(s) seleccionados: ${parametroSeleccionado.value}`,
        `Periodo: ${periodoTexto}`,
        `Alineación: ${alinearSemanas.value ? 'Semanas desde fecha de siembra' : 'Fechas calendario'}`,
      ];
      resumenL.forEach(line => { doc.text(doc.splitTextToSize(line, CONTENT_W), M, y); y += 12; });
      if (comparar.value) {
        const resComp = `Comparación: ${grupos.value.filter(g=>g.ids.length).map(g=>`G${g.gid}(${g.ids.length})`).join(' vs ')}`;
        doc.text(doc.splitTextToSize(resComp, CONTENT_W), M, y); y += 12;
      }
      y += 4;

      // ====== Tablas de grupos / siembras (arriba, en lugar de una línea larga) ======
      const rubroTexto = parametroSeleccionado.value === 'Todos los rubros'
        ? 'Todos los rubros'
        : parametroSeleccionado.value;

      const putGroupTable = (title, rows) => {
        setFont('helvetica', 10, 'bold');
        if (y + 26 > PAGE_H - M) { doc.addPage(); y = M; }
        doc.text(title, M, y); y += 6;
        autoTable(doc, {
          startY: y + 8,
          margin: { left: M, right: M },
          styles: { font: 'helvetica', fontSize: 9, cellPadding: 5, overflow: 'linebreak' },
          headStyles: { fillColor: [40, 167, 69], textColor: 255, halign: 'center' },
          bodyStyles: { halign: 'center' },
          columnStyles: {
            0: { cellWidth: CONTENT_W * 0.28 }, // Estanque
            1: { cellWidth: CONTENT_W * 0.16 }, // Inicio
            2: { cellWidth: CONTENT_W * 0.16 }, // Fin
            3: { cellWidth: CONTENT_W * 0.22 }, // Especie
            4: { cellWidth: CONTENT_W * 0.18 }, // Rubro
          },
          head: [['Estanque', 'Inicio', 'Fin', 'Especie', 'Rubro']],
          body: rows
        });
        y = doc.lastAutoTable.finalY + 12;
      };

      if (comparar.value) {
        grupos.value.forEach(g => {
          if (!g.ids.length) return;
          const rows = g.ids.map(id => {
            const s = siembraPorId.value.get(id);
            const estanque = nombreEstanquePorId.value.get(s.estanque) || s.estanque;
            const inicio = firstDatoFecha(id);
            const fin = lastDatoFecha(id);
            return [estanque, inicio, fin, s.especie, rubroTexto];
          });
          putGroupTable(`Grupo ${g.gid}`, rows);
        });
      } else {
        const rows = siembrasSeleccionadas.value.map(id => {
          const s = siembraPorId.value.get(id);
          const estanque = nombreEstanquePorId.value.get(s.estanque) || s.estanque;
          const inicio = firstDatoFecha(id);
          const fin = lastDatoFecha(id);
          return [estanque, inicio, fin, s.especie, rubroTexto];
        });
        putGroupTable('Siembras', rows);
      }

      // ====== Gráfico (tamaño fijo) ======
      const CHART_H = 240;
      if (y + CHART_H + 16 > PAGE_H - M) { doc.addPage(); y = M; }
      const canvas = document.getElementById('grafico');
      if (canvas) {
        const imgData = canvas.toDataURL('image/png', 1.0);
        doc.addImage(imgData, 'PNG', M, y, CONTENT_W, CHART_H, '', 'FAST');
        y += CHART_H + 16;
      }

      // ====== Distribuciones (tablas) ======
      const putDistribTable = (title, rows) => {
        setFont('helvetica', 10, 'bold');
        if (y + 26 > PAGE_H - M) { doc.addPage(); y = M; }
        doc.text(title, M, y); y += 6;
        autoTable(doc, {
          startY: y + 8,
          margin: { left: M, right: M },
          styles: { font: 'helvetica', fontSize: 9, cellPadding: 5 },
          headStyles: { fillColor: [40, 167, 69], textColor: 255, halign: 'center' },
          bodyStyles: { halign: 'center' },
          columnStyles: { 0: { cellWidth: CONTENT_W * 0.6 }, 1: { cellWidth: CONTENT_W * 0.4 } },
          head: [['Rango (gr)', 'Cantidad']],
          body: rows
        });
        y = doc.lastAutoTable.finalY + 12;
      };

      if (comparar.value) {
        for (const [nombreGrupo, mapaFechas] of Object.entries(distribucionTallasGrupos.value)) {
          for (const [fecha, segmentos] of Object.entries(mapaFechas)) {
            putDistribTable(`Distribución de Tallas — ${nombreGrupo} — ${fecha}`,
              segmentos.map(s => [s.etiqueta, s.cantidad]));
          }
        }
      } else {
        for (const [fecha, segmentos] of Object.entries(distribucionTallas.value)) {
          putDistribTable(`Distribución de Tallas — ${fecha}`,
            segmentos.map(s => [s.etiqueta, s.cantidad]));
        }
      }

      // ====== Encabezado repetido y pie de página con numeración ======
      const pageCount = doc.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        drawHeader(i);
        doc.setPage(i);
        setFont('helvetica', 9);
        doc.setTextColor(120);
        doc.text(`Página ${i} de ${pageCount}`, PAGE_W / 2, PAGE_H - 12, { align: 'center' });
        doc.setTextColor(0);
      }

      if (preview) {
        const blob = doc.output('blob');
        if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
        const url = URL.createObjectURL(blob);
        return url;
      } else {
        doc.save(`reporte_crecimiento_${Date.now()}.pdf`);
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

    // Reacciones
    watch(siembrasSeleccionadas, obtenerRubros);

    onMounted(async () => {
      await Promise.all([obtenerEstanques(), obtenerTodasLasSiembras()]);
    });

    return {
      // datos
      estanques, todasSiembras, datos, rubros, farmName,

      // selección y ui
      siembrasSeleccionadas, busquedaEstanque, busquedaSiembra, expandido,

      // grupos
      GRUPO_MAX, comparar, asignacionGrupo, grupos, hayGruposConMiembros,
      grupoDeSiembra, toggleGrupo, removerDeGrupo, vaciarGrupo,

      // listas/etiquetas
      estanquesFiltrados, siembrasDeEstanqueFiltradas,
      formatDate, etiquetaSiembra, etiquetaSiembraPorId, conteoSiembras, nickSiembra, lastDatoFecha,

      // acciones UI
      toggleExpand, seleccionarTodasDeEstanque, limpiarDeEstanque,
      seleccionarTodasVisibles, limpiarSeleccion, quitarSiembra,

      // opciones
      parametrosActuales, parametroSeleccionado, periodoSeleccionado, periodos, alinearSemanas,

      // reporte & gráfico
      distribucionTallas, distribucionTallasGrupos, actualizarGrafico, exportarReporte,
      chartInstances, tituloSerie,

      // preview
      showPreview, previewUrl, mostrarVistaPrevia, cerrarPreview,

      // mapas rubros
      idRubroPorEtiqueta, etiquetaPorIdRubro
    };
  }
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
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

.form-seleccion { margin-bottom: 20px; }
.form-group { margin-bottom: 16px; display: flex; flex-direction: column; }
label { font-weight: 600; margin-bottom: 8px; color: #444; font-size: 14px; }

select, .input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd; border-radius: 8px;
  font-size: 14px; background: #f8f9fa;
  transition: all .2s ease-in-out;
}
.input.small { padding: 8px 10px; font-size: 13px; }
select:focus, .input:focus { border-color: #28a745; outline: none; box-shadow: 0 0 5px rgba(40,167,69,.35); }

/* Bloques una columna */
.one-col .block { margin-bottom: 16px; }
.card { border: 1px solid #eee; border-radius: 12px; padding: 12px; }
.block-title { margin-bottom: 8px; display: block; }

/* Lista de estanques/siembras */
.list { list-style: none; margin: 0; padding: 0; }
.ponds { margin-top: 10px; }
.pond-row { border: 1px solid #eee; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
.pond-row-main {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  padding: 6px 4px; border-radius: 8px;
}
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
.siembras-list li {
  padding: 6px 0; border-bottom: 1px dashed #f0f0f0;
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
}

/* Botones de grupos */
.grp-buttons { display: inline-flex; gap: 4px; flex-wrap: wrap; }
.grp-btn {
  border: 1px solid #cfd; border-radius: 6px; padding: 4px 6px; font-size: 12px;
  cursor: pointer; background: #fff; min-width: 28px; text-align: center;
}
.grp-btn.active { background: #eaffef; border-color: #28a745; font-weight: 700; }

/* Chips seleccionadas */
.chips { display: flex; gap: 8px; flex-wrap: wrap; margin: 6px 0 10px; }
.chip {
  background: #f0fff4; border: 1px solid #d1f5dc; color: #1d7f3b;
  padding: 6px 10px; border-radius: 999px; font-size: 12px; display: inline-flex; gap: 6px; align-items: center;
}
.chip.tiny { font-size: 11px; padding: 4px 8px; }
.chip-x { background: transparent; border: none; cursor: pointer; font-size: 14px; line-height: 1; color: #1d7f3b; }

.quick-actions { display: flex; gap: 8px; margin: 8px 0 4px; flex-wrap: wrap; }

/* Pequeños botones y variantes */
.btn-sm { background: #28a745; color: #fff; border: none; padding: 8px 10px; border-radius: 8px; font-size: 12px; }
.btn-sm.outline { background:#fff; color:#28a745; border:1px solid #28a745; }

/* Toggles */
.toggles { gap: 10px; }
.toggle { display: flex; gap: 8px; align-items: center; cursor: pointer; }
.toggle input { transform: scale(1.1); }

/* Chart: responsive y más alto */
.chart-header {
  display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px;
}
.chart-wrap { position: relative; width: 100%; height: clamp(460px, 70vh, 880px); }

canvas { margin-top: 0; max-width: 100%; }
.grafico-individual { margin-bottom: 30px; }

/* Tablas */
table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
th, td { padding: 8px; border: 1px solid #ddd; text-align: center; }

/* Botones generales */
button { transition: transform .1s ease-in-out; }
button:hover { transform: scale(1.02); }
button:active { transform: scale(0.98); }
.btn-generar { margin-top: 12px; background: #28a745; color: #fff; border: none; padding: 12px 15px; border-radius: 8px; font-weight: 700; }
.btn-generar.outline { background:#fff; color:#28a745; border:1px solid #28a745; }

/* Fila de botones PDF */
.btn-row { display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px; }

/* Transición acordeones */
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.hint { color: #666; font-size: 12px; }
.grupo-line { display:flex; align-items:center; gap:8px; flex-wrap: wrap; margin: 6px 0; }

/* Modal preview */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.35);
  display: flex; align-items: center; justify-content: center; z-index: 9999;
}
.modal {
  width: min(1000px, 92vw); height: min(85vh, 900px);
  background: #fff; border-radius: 12px; overflow: hidden;
  box-shadow: 0 10px 40px rgba(0,0,0,.2); display: flex; flex-direction: column;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; border-bottom: 1px solid #eee;
}
.pdf-frame { width: 100%; height: 100%; border: 0; }
</style>
