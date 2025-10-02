<template>
  <div class="min-h-screen bg-gradient-to-b from-white to-slate-100 dark:from-slate-950 dark:to-slate-900 text-slate-900 dark:text-slate-100">
    <!-- Header -->
    <header class="sticky top-0 z-30 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-slate-900/50 border-b border-slate-200/60 dark:border-slate-700/60">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 class="text-xl sm:text-2xl font-bold tracking-tight flex items-center gap-2">
          <span class="inline-block h-7 w-7 rounded-xl bg-blue-600/10 ring-1 ring-blue-600/30 flex items-center justify-center">
            <span class="h-2 w-2 rounded-full bg-blue-600"></span>
          </span>
          Proyección de Siembra
        </h1>
        <div class="hidden sm:flex items-center gap-2">
          <button type="button" @click="exportarCSV" :disabled="!filas.length"
                  class="btn-primary" :class="{'btn-disabled': !filas.length}">Exportar CSV</button>
          <button type="button" @click="resetear" class="btn-muted">Resetear</button>
        </div>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-7xl mx-auto px-4 py-6 space-y-6">
      <!-- Card: Parámetros -->
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">Parámetros iniciales</h2>
          <p class="card-sub">Define el horizonte y las condiciones iniciales de la proyección.</p>
        </div>
        <form @submit.prevent="generarTabla" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="field">
            <label>Semanas de proyección</label>
            <input v-model.number="form.semanas" type="number" min="1" required class="input" />
          </div>
          <div class="field">
            <label>Superficie de siembra (m²)</label>
            <input v-model.number="form.superficie_m2" type="number" step="0.0001" min="0.0001" required class="input" />
          </div>
          <div class="field">
            <label>Organismos sembrados (No.)</label>
            <input v-model.number="form.organismos_iniciales" type="number" min="1" required class="input" />
          </div>
          <div class="field">
            <label>Talla inicial (g)</label>
            <input v-model.number="form.talla_g" type="number" step="0.01" min="0.01" required class="input" />
          </div>
          <div class="field">
            <label>Fecha de inicio (opcional)</label>
            <input v-model="form.fecha_inicio" type="date" class="input" />
          </div>
          <div class="flex items-end gap-3 sm:col-span-2 lg:col-span-3">
            <button type="submit" class="btn-primary">Generar tabla</button>
            <button type="button" class="btn-muted" @click="resetear">Resetear</button>
            <button type="button" class="btn-ghost sm:hidden" @click="exportarCSV" :disabled="!filas.length" :class="{'btn-disabled': !filas.length}">Exportar CSV</button>
          </div>
        </form>
      </section>

      <!-- Card: Tabla (Desktop / Tablet) -->
      <section v-if="filas.length" class="card md:hidden">
        <div class="card-header flex items-center justify-between">
          <h2 class="card-title">Proyección semanal</h2>
          <p class="card-sub">Edite los porcentajes y tallas; todo se recalcula al vuelo.</p>
        </div>
        <div class="table-wrapper">
          <table class="tbl">
            <thead>
              <tr>
                <th class="sticky-col">Sem</th>
                <th class="sticky-col-2">Fecha</th>
                <th>% Alimento por biomasa</th>
                <th>% Superv (acum)</th>
                <th>Talla (g)</th>
                <th class="text-right">Org vivos</th>
                <th class="text-right">Org/m²</th>
                <th class="text-right">Crec. semanal (g)</th>
                <th class="text-right">Crec. diario (g)</th>
                <th class="text-right">Biomasa (g)</th>
                <th class="text-right">Alimento diario (g)</th>
                <th class="text-right">Alimento semanal (g)</th>
                <th class="text-right">Alimento acumulado (g)</th>
                <th class="text-right">FCA</th>
                <th class="text-right">g/m³</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, idx) in filas" :key="idx">
                <td class="sticky-col">{{ r.semana }}</td>
                <td class="sticky-col-2">{{ r.fecha ?? '—' }}</td>
                <td>
                  <input :id="inputId('biomasa', idx)" type="number" step="0.01" class="input input-cell"
                         v-model.number="r.pct_biomasa" @input="recalcularDesde(idx)" @keydown.tab.prevent="focusNext(idx, 'biomasa')" />
                </td>
                <td>
                  <input :id="inputId('superv', idx)" type="number" step="0.01" min="0" :max="maxSuperv(idx)" class="input input-cell"
                         v-model.number="r.pct_superv" @input="onSupervInput(idx)" @keydown.tab.prevent="focusNext(idx, 'superv')" />
                </td>
                <td>
                  <input :id="inputId('talla', idx)" type="number" step="0.01" min="0" class="input input-cell"
                         v-model.number="r.talla_g" @input="onTallaInput(idx)" @keydown.tab.prevent="focusNext(idx, 'talla')" />
                </td>
                <td class="text-right">{{ fmt0(r.organismos_vivos) }}</td>
                <td class="text-right">{{ fmt2(r.org_m2) }}</td>
                <td class="text-right">{{ fmt2(r.crec_semanal_g) }}</td>
                <td class="text-right">{{ fmt4(r.crec_diario_g) }}</td>
                <td class="text-right">{{ fmt2(r.biomasa_g) }}</td>
                <td class="text-right">{{ fmt2(r.alimento_diario_g) }}</td>
                <td class="text-right">{{ fmt2(r.alimento_semanal_g) }}</td>
                <td class="text-right">{{ fmt2(r.alimento_acum_g) }}</td>
                <td class="text-right">{{ fmt4(r.fca) }}</td>
                <td class="text-right">{{ fmt2(r.g_por_m3) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td class="sticky-col text-right" colspan="9">Totales</td>
                <td class="text-right">{{ fmt2(totalBiomasa_g) }}</td>
                <td></td>
                <td class="text-right">{{ fmt2(totalAlimentoSem_g) }}</td>
                <td class="text-right">{{ fmt2(totalAlimentoAcum_g) }}</td>
                <td></td>
                <td class="text-right">{{ fmt2(total_g_m3) }}</td>
              </tr>
            </tfoot>
          </table>
          <!-- Scroll shadows -->
          <div class="scroll-shadow left" aria-hidden="true"></div>
          <div class="scroll-shadow right" aria-hidden="true"></div>
        </div>
      </section>

      <!-- Card: Vista móvil (Cards) -->
      <section v-if="filas.length" class="card md:hidden">
        <div class="card-header">
          <h2 class="card-title">Proyección semanal (móvil)</h2>
          <p class="card-sub">Diseño compacto para captura rápida en pantalla chica.</p>
        </div>
        <ul class="space-y-4">
          <li v-for="(r, idx) in filas" :key="'m'+idx" class="row-card">
            <div class="flex items-center justify-between">
              <div class="font-semibold">Semana {{ r.semana }}</div>
              <div class="text-slate-500 text-sm">{{ r.fecha ?? '—' }}</div>
            </div>
            <div class="grid grid-cols-2 gap-3 mt-3">
              <div class="field small">
                <label>% Ali. por biomasa</label>
                <input type="number" step="0.01" class="input"
                       v-model.number="r.pct_biomasa" @input="recalcularDesde(idx)" />
              </div>
              <div class="field small">
                <label>% Superv (acum)</label>
                <input type="number" step="0.01" min="0" :max="maxSuperv(idx)" class="input"
                       v-model.number="r.pct_superv" @input="onSupervInput(idx)" />
              </div>
              <div class="field small col-span-2">
                <label>Talla (g)</label>
                <input type="number" step="0.01" min="0" class="input"
                       v-model.number="r.talla_g" @input="onTallaInput(idx)" />
              </div>
            </div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-sm">
              <div class="stat"><span>Org vivos</span><strong>{{ fmt0(r.organismos_vivos) }}</strong></div>
              <div class="stat"><span>Org/m²</span><strong>{{ fmt2(r.org_m2) }}</strong></div>
              <div class="stat"><span>Crec/sem (g)</span><strong>{{ fmt2(r.crec_semanal_g) }}</strong></div>
              <div class="stat"><span>Crec/día (g)</span><strong>{{ fmt4(r.crec_diario_g) }}</strong></div>
              <div class="stat"><span>Biomasa (g)</span><strong>{{ fmt2(r.biomasa_g) }}</strong></div>
              <div class="stat"><span>Ali/día (g)</span><strong>{{ fmt2(r.alimento_diario_g) }}</strong></div>
              <div class="stat"><span>Ali/sem (g)</span><strong>{{ fmt2(r.alimento_semanal_g) }}</strong></div>
              <div class="stat"><span>Ali acumul. (g)</span><strong>{{ fmt2(r.alimento_acum_g) }}</strong></div>
              <div class="stat"><span>FCA</span><strong>{{ fmt4(r.fca) }}</strong></div>
              <div class="stat"><span>g/m³</span><strong>{{ fmt2(r.g_por_m3) }}</strong></div>
            </div>
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>

<script setup>
import { reactive, ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'

const form = reactive({
  semanas: 12,
  superficie_m2: 0.8,        // m²
  organismos_iniciales: 32,
  talla_g: 2.35,              // g
  fecha_inicio: '',           // yyyy-mm-dd
})

/* Filas: estructura completa */
const filas = ref([])

function generarTabla () {
  const semanas = Math.max(1, Number(form.semanas || 0))
  const baseFecha = form.fecha_inicio ? new Date(form.fecha_inicio + 'T00:00:00') : null

  filas.value = Array.from({ length: semanas }, (_, i) => {
    const semana = i + 1
    const fecha = baseFecha ? addDays(baseFecha, i * 7).toISOString().slice(0, 10) : null
    return {
      semana, fecha,
      pct_biomasa: 0,
      pct_superv: 100, // acumulado desde inicio
      talla_g: i === 0 ? toNum(form.talla_g) : toNum(form.talla_g),
      organismos_vivos: 0,
      org_m2: 0,
      crec_semanal_g: 0,
      crec_diario_g: 0,
      biomasa_g: 0,
      alimento_diario_g: 0,
      alimento_semanal_g: 0,
      alimento_acum_g: 0,
      fca: 0,
      g_por_m3: 0,
    }
  })
  enforceSurvivalChain(0, true)
  enforceTallaChain(0)
  recalcularDesde(0)
}

/* ===== Supervivencia acumulada ===== */
function maxSuperv (idx) { return idx === 0 ? 100 : toNum(filas.value[idx - 1]?.pct_superv ?? 100) }
function onSupervInput (idx) {
  const maxAllowed = maxSuperv(idx)
  let v = clamp(toNum(filas.value[idx].pct_superv), 0, maxAllowed)
  const decreased = v < maxAllowed
  filas.value[idx].pct_superv = v
  for (let j = idx + 1; j < filas.value.length; j++) {
    if (decreased) filas.value[j].pct_superv = v
    filas.value[j].pct_superv = Math.min(filas.value[j].pct_superv, filas.value[j - 1].pct_superv)
  }
  recalcularDesde(0)
}
function enforceSurvivalChain (startIdx = 0, forceEqualForward = false) {
  for (let i = startIdx; i < filas.value.length; i++) {
    const maxAllowed = maxSuperv(i)
    let v = clamp(toNum(filas.value[i].pct_superv), 0, maxAllowed)
    filas.value[i].pct_superv = v
    if (forceEqualForward && i < filas.value.length - 1) {
      for (let j = i + 1; j < filas.value.length; j++) filas.value[j].pct_superv = v
    }
  }
}

/* ===== Talla (no decreciente) ===== */
function onTallaInput (idx) {
  if (idx === 0) {
    const base = toNum(form.talla_g)
    if (toNum(filas.value[0].talla_g) < base) filas.value[0].talla_g = base
  } else {
    const prev = toNum(filas.value[idx - 1].talla_g)
    if (toNum(filas.value[idx].talla_g) < prev) filas.value[idx].talla_g = prev
  }
  for (let j = idx + 1; j < filas.value.length; j++) {
    if (toNum(filas.value[j].talla_g) < toNum(filas.value[j - 1].talla_g)) {
      filas.value[j].talla_g = filas.value[j - 1].talla_g
    }
  }
  recalcularDesde(idx)
}
function enforceTallaChain (startIdx = 0) {
  for (let i = startIdx; i < filas.value.length; i++) {
    if (i === 0) filas.value[i].talla_g = Math.max(toNum(filas.value[i].talla_g), toNum(form.talla_g))
    else filas.value[i].talla_g = Math.max(toNum(filas.value[i].talla_g), toNum(filas.value[i - 1].talla_g))
  }
}

/* ===== Recalcular métricas ===== */
function recalcularDesde (startIdx) {
  const N0 = toNum(form.organismos_iniciales)
  const area = Math.max(toNum(form.superficie_m2), 0.0001)

  for (let i = Math.max(0, startIdx); i < filas.value.length; i++) {
    const r = filas.value[i]

    // Organismos vivos por % superv acumulada
    const organismos = N0 * clamp(toNum(r.pct_superv) / 100, 0, 1)

    // Talla: no decreciente
    if (i === 0) r.talla_g = Math.max(toNum(r.talla_g), toNum(form.talla_g))
    else r.talla_g = Math.max(toNum(r.talla_g), toNum(filas.value[i - 1].talla_g))

    // Crecimientos
    const talla_prev = i === 0 ? toNum(form.talla_g) : toNum(filas.value[i - 1].talla_g)
    const crec_semanal_g = toNum(r.talla_g) - talla_prev
    const crec_diario_g = crec_semanal_g / 7

    // Biomasa en g
    const biomasa_g = organismos * toNum(r.talla_g)

    // Org por m²
    const org_m2 = organismos / area

    // Alimentos (g). % alimento por biomasa (diario) aplicado a la biomasa del día
    const pctAli = Math.max(0, toNum(r.pct_biomasa) / 100)
    const alimento_diario_g = biomasa_g * pctAli
    const alimento_semanal_g = alimento_diario_g * 7
    const alimento_acum_g = (i === 0 ? 0 : filas.value[i - 1].alimento_acum_g) + alimento_semanal_g

    // FCA & g/m³ (según definiciones indicadas por el usuario / Excel actual)
    const fca = biomasa_g * alimento_acum_g
    const g_por_m3 = area * biomasa_g

    r.organismos_vivos = organismos
    r.org_m2 = org_m2
    r.crec_semanal_g = crec_semanal_g
    r.crec_diario_g = crec_diario_g
    r.biomasa_g = biomasa_g
    r.alimento_diario_g = alimento_diario_g
    r.alimento_semanal_g = alimento_semanal_g
    r.alimento_acum_g = alimento_acum_g
    r.fca = fca
    r.g_por_m3 = g_por_m3
  }
}

/* ===== Totales ===== */
const totalBiomasa_g = computed(() => filas.value.reduce((a, r) => a + toNum(r.biomasa_g), 0))
const totalAlimentoSem_g = computed(() => filas.value.reduce((a, r) => a + toNum(r.alimento_semanal_g), 0))
const totalAlimentoAcum_g = computed(() => (filas.value.length ? toNum(filas.value[filas.value.length - 1].alimento_acum_g) : 0))
const total_g_m3 = computed(() => filas.value.reduce((a, r) => a + toNum(r.g_por_m3), 0))

/* ===== Utilidades ===== */
function toNum (v) { const n = Number(v); return Number.isFinite(n) ? n : 0 }
function clamp (v, min, max) { return Math.min(max, Math.max(min, v)) }
function addDays (date, days) { const d = new Date(date); d.setDate(d.getDate() + days); return d }
function fmt0 (n) { return Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 }) }
function fmt2 (n) { return Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
function fmt4 (n) { return Number(n).toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 }) }

/* ===== Navegación TAB por columna (vista tabla) ===== */
function inputId (field, idx) { return `${field}-${idx}` }
function focusNext (idx, field) {
  nextTick(() => { const el = document.getElementById(inputId(field, idx + 1)); if (el) el.focus() })
}

/* ===== Acciones ===== */
function exportarCSV () {
  if (!filas.value.length) return
  const header = [
    'Semana','Fecha','%AlimentoBiomasa','%Superv_acum','Talla_g',
    'OrganismosVivos','Org_m2','CrecSem_g','CrecDia_g','Biomasa_g',
    'AliDiario_g','AliSemanal_g','AliAcum_g','FCA','g_m3'
  ]
  const rows = filas.value.map(r => ([
    r.semana, r.fecha ?? '', r.pct_biomasa, r.pct_superv, round(r.talla_g,4),
    Math.round(r.organismos_vivos), round(r.org_m2,4), round(r.crec_semanal_g,4),
    round(r.crec_diario_g,6), round(r.biomasa_g,4), round(r.alimento_diario_g,4),
    round(r.alimento_semanal_g,4), round(r.alimento_acum_g,4), round(r.fca,6), round(r.g_por_m3,4)
  ]))
  const csv = [header, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = 'Proyeccion_Siembra.csv'; a.click()
  URL.revokeObjectURL(url)
}
function round (v, d=2){ return Number.parseFloat((+v).toFixed(d)) }
function resetear () { filas.value = [] }

/* Optional: color scheme sync */
const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)')
function applyDark(e){ document.documentElement.classList.toggle('dark', e.matches) }
onMounted(()=>{ if (prefersDark) { applyDark(prefersDark); prefersDark.addEventListener('change', applyDark) } })
onBeforeUnmount(()=>{ if (prefersDark) prefersDark.removeEventListener('change', applyDark) })
</script>

<style scoped>
/* Fuente base */
:host {
  font-family: 'Poppins', sans-serif;
  color: #333;
}

/* ---------- Contenedores ---------- */
.card {
  max-width: auto;
  margin: 24px auto;
  padding: 22px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transition: box-shadow .2s ease, transform .15s ease;
}
.card:hover { box-shadow: 0 6px 16px rgba(0,0,0,0.12); transform: translateY(-1px); }

.card-header { margin-bottom: 12px; }
.card-title { font-size: 20px; font-weight: 600; color: #222; margin: 0 0 4px; text-align: left; }
.card-sub { font-size: 13px; color: #6b7280; margin: 0; }

/* ---------- Campos ---------- */
.field { display: flex; flex-direction: column; gap: 6px; }
.field > label { font-weight: 600; font-size: 14px; color: #444; }

.input {
  width: 100%; padding: 10px 12px;
  border: 1px solid #ddd; border-radius: 8px;
  font-size: 14px; background: #f8f9fa;
  transition: border-color .2s ease, box-shadow .2s ease, background .2s ease;
}
.input:focus {
  border-color: #28a745; background: #fff; outline: none;
  box-shadow: 0 0 0 3px rgba(40,167,69,0.15);
}

/* celdas de tabla editables: ancho y alineación */
.input-cell { width: 8rem; text-align: right; }

/* ---------- Botones ---------- */
.btn-primary,
.btn-muted,
.btn-ghost {
  padding: 10px 14px; border-radius: 10px; font-weight: 600;
  font-size: 14px; cursor: pointer; border: none; transition: transform .1s ease, filter .2s ease, background .2s ease;
}

.btn-primary { background: #28a745; color: #fff; }
.btn-primary:hover { filter: brightness(1.03); transform: translateY(-1px); }
.btn-primary:active { transform: translateY(0); }

.btn-muted { background: #eef2f3; color: #334155; }
.btn-muted:hover { background: #e6ecee; }

.btn-ghost { background: transparent; color: #334155; }
.btn-ghost:hover { background: #f1f5f9; }

.btn-disabled { opacity: .5; pointer-events: none; }

/* ---------- Tabla grande (desktop/tablet) ---------- */
.table-wrapper { position: relative; overflow: auto; border-radius: 12px; border: 1px solid #e5e7eb; }

.tbl { width: 100%; border-collapse: collapse; font-size: 14px; background: #fff; }
.tbl thead th {
  position: sticky; top: 0; z-index: 2;
  background: #f8f9fa; color: #374151;
  font-weight: 600; text-align: left; padding: 10px 12px;
  border-bottom: 1px solid #e5e7eb;
}
.tbl tbody td { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; }
.tbl tbody tr:hover td { background: #f3fdf6; }
.tbl tfoot td {
  background: #f8f9fa; font-weight: 600; padding: 10px 12px;
  border-top: 1px solid #e5e7eb;
}

/* Columnas fijas de la izquierda */
.sticky-col { position: sticky; left: 0; z-index: 3; background: inherit; }
.sticky-col-2 { position: sticky; left: 5.5rem; z-index: 3; background: inherit; }

/* Sombras laterales al hacer scroll horizontal */
.scroll-shadow { position: absolute; top: 0; bottom: 0; width: 26px; pointer-events: none; }
.scroll-shadow.left { left: 0; background: linear-gradient(to right, rgba(0,0,0,.10), transparent); }
.scroll-shadow.right { right: 0; background: linear-gradient(to left, rgba(0,0,0,.10), transparent); }

/* ---------- Vista móvil (cards) ---------- */
.row-card {
  border-radius: 14px; border: 1px solid #e5e7eb;
  background: #ffffff; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat {
  display: flex; align-items: center; justify-content: space-between;
  background: #f8fafc; border: 1px solid #eef2f7; border-radius: 10px;
  padding: 8px 10px;
}
.stat span { color: #64748b; }
.stat strong { color: #111827; }

/* ---------- Dark mode básico (respetando .dark en <html>) ---------- */
:global(.dark) .card { background: #0f172a; color: #e5e7eb; border-color: #273449; }
:global(.dark) .tbl { background: #0f172a; }
:global(.dark) .tbl thead th,
:global(.dark) .tbl tfoot td { background: rgba(30,41,59,.85); color: #e5e7eb; border-color: #334155; }
:global(.dark) .tbl tbody td { border-color: #1f2937; }
:global(.dark) .row-card { background: #0f172a; border-color: #273449; }
:global(.dark) .stat { background: #111827; border-color: #1f2937; }
:global(.dark) .btn-muted { background: #1f2937; color: #e5e7eb; }
:global(.dark) .btn-ghost:hover { background: #1f2937; }
:global(.dark) .input { background: #0b1220; border-color: #273449; color: #e5e7eb; }
:global(.dark) .input:focus { box-shadow: 0 0 0 3px rgba(40,167,69,0.23); }

/* ---------- Responsivo ---------- */
@media (max-width: 768px) {
  .card { padding: 18px; }
  .card-title { font-size: 18px; }
  .btn-primary, .btn-muted, .btn-ghost { font-size: 13px; padding: 9px 12px; }
  .input { font-size: 13px; padding: 9px 10px; }
  .input-cell { width: 7rem; }
  .tbl { font-size: 13px; }
}
</style>

