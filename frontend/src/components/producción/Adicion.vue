<template>
  <section class="container">
    <!-- Card encabezado -->
    <div class="card" role="region" aria-labelledby="add-title">
      <div class="card__header">
        <h2 id="add-title" class="card__title">Adición de Organismos</h2>
        <p class="card__sub">Registra el alta de organismos a una siembra existente.</p>
      </div>

      <form @submit.prevent="agregarOrganismos" novalidate>
        <!-- Siembra -->
        <div class="field">
          <label for="siembra">Selecciona la siembra</label>
          <select id="siembra" v-model="adicion.siembra" class="select" required>
            <option value="" disabled>— Selecciona —</option>
            <option
              v-for="s in siembrasFiltradas"
              :key="s.id"
              :value="s.id"
            >
              {{ s.nombre }} — {{ s.especie }}
            </option>
          </select>
        </div>

        <!-- Número de organismos -->
        <div class="field">
          <label for="numero-organismos">Número de organismos a agregar</label>
          <input
            id="numero-organismos"
            v-model.number="adicion.numeroOrganismos"
            class="input"
            type="number"
            inputmode="numeric"
            min="1"
            placeholder="Ej. 5000"
            required
          />
        </div>

        <!-- Peso promedio -->
        <div class="field">
          <label for="peso-promedio">Peso promedio por organismo (g)</label>
          <input
            id="peso-promedio"
            v-model.number="adicion.pesoPromedio"
            class="input"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="Ej. 0.30"
            required
          />
        </div>

        <!-- Fecha -->
        <div class="field">
          <label for="fecha-adicion">Fecha de adición</label>
          <input
            id="fecha-adicion"
            v-model="adicion.fecha"
            class="input"
            type="date"
            :max="hoy"
            required
          />
        </div>

        <!-- Resumen dinámico -->
        <div class="row-card mt-2">
          <div class="stat">
            <span>Biomasa a agregar (kg)</span>
            <strong>{{ formatNum(biomasaKg) }}</strong>
          </div>
        </div>

        <!-- Acciones -->
        <div class="mt-3" style="display:flex; gap:8px; flex-wrap:wrap;">
          <button type="submit" class="btn btn--accent" :disabled="loading">
            {{ loading ? 'Agregando…' : 'Agregar Organismos' }}
          </button>
          <button type="button" class="btn btn--outline" @click="limpiar" :disabled="loading">
            Limpiar
          </button>
        </div>
      </form>
    </div>

    <!-- Tabla (opcional) último registro añadido en sesión -->
    <div v-if="ultimo" class="card mt-3" role="region" aria-labelledby="last-add">
      <div class="card__header">
        <h3 id="last-add" class="card__title">Última adición registrada</h3>
        <p class="card__sub">Solo visible en esta sesión.</p>
      </div>

      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Siembra</th>
              <th>Especie</th>
              <th class="text-right">Organismos</th>
              <th class="text-right">Peso prom. (g)</th>
              <th class="text-right">Biomasa (kg)</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ ultimo.siembraNombre }}</td>
              <td>{{ ultimo.especie }}</td>
              <td class="text-right">{{ formatNum(ultimo.numeroOrganismos) }}</td>
              <td class="text-right">{{ formatNum(ultimo.pesoPromedio) }}</td>
              <td class="text-right">{{ formatNum(ultimo.biomasaKg) }}</td>
              <td>{{ ultimo.fecha }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from '@/services/axios'

/** Endpoints (ajústalos si tu API difiere) */
const ENDPOINTS = {
  siembras: '/siembra/',
  adicion: '/adicion/', // POST esperado: { siembra, numero_organismos, peso_promedio_g, fecha }
}

/** Helpers */
const toNum = (v) =>
  v === null || v === undefined || v === '' || Number.isNaN(Number(v)) ? null : Number(v)

function mapSiembra(api) {
  return {
    id: api.id ?? api.id_siembra ?? api.pk,
    nombre: api.nombre ?? api.alias ?? `Siembra ${api.id ?? ''}`,
    especie:
      api.especie ??
      api.especie_nombre ??
      api.especie_cientifica ??
      api.especie_common ??
      '',
    activa:
      api.fecha_cosecha == null && (api.estado === 1 || api.status === 1 || api.activa === true),
    acuicola: toNum(api.acuicola ?? api.acuicola_id),
  }
}

export default {
  name: 'AdicionOrganismos',
  setup() {
    const siembras = ref([])
    const loading = ref(false)
    const ultimo = ref(null)

    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const acuicolaId = user?.acuicola ?? null

    const hoy = new Date().toISOString().slice(0, 10)

    const adicion = reactive({
      siembra: '',
      numeroOrganismos: null,
      pesoPromedio: null, // gramos
      fecha: hoy,
    })

    const siembrasFiltradas = computed(() => {
      // Prioriza siembras activas y de la misma acuícola (si viene)
      return siembras.value
        .filter((s) => (acuicolaId == null || s.acuicola == null || s.acuicola === acuicolaId))
        .sort((a, b) => Number(b.activa) - Number(a.activa))
    })

    const biomasaKg = computed(() => {
      const n = Number(adicion.numeroOrganismos || 0)
      const g = Number(adicion.pesoPromedio || 0)
      const kg = (n * g) / 1000
      return Number.isFinite(kg) ? kg : 0
    })

    function formatNum(n) {
      const x = Number(n || 0)
      return Number.isFinite(x)
        ? x.toLocaleString(undefined, { maximumFractionDigits: 2 })
        : '0'
    }

    async function fetchSiembras() {
      try {
        const res = await axios.get(ENDPOINTS.siembras)
        const data = Array.isArray(res.data) ? res.data : res.data.results || []
        siembras.value = data.map(mapSiembra)
      } catch (e) {
        console.error('Error al cargar siembras', e)
        siembras.value = []
      }
    }

    function validar() {
      if (!adicion.siembra) return 'Selecciona una siembra.'
      if (!adicion.numeroOrganismos || adicion.numeroOrganismos < 1)
        return 'Ingresa el número de organismos (mínimo 1).'
      if (!adicion.pesoPromedio || adicion.pesoPromedio <= 0)
        return 'Ingresa el peso promedio en gramos (mayor a 0).'
      if (!adicion.fecha) return 'Selecciona la fecha.'
      return ''
    }

    async function agregarOrganismos() {
      const msg = validar()
      if (msg) {
        alert(msg)
        return
      }

      loading.value = true
      try {
        const payload = {
          siembra: adicion.siembra,
          numero_organismos: Number(adicion.numeroOrganismos),
          peso_promedio_g: Number(adicion.pesoPromedio),
          fecha: adicion.fecha,
        }
        // Llama a tu API real:
        await axios.post(ENDPOINTS.adicion, payload)

        // Cache del último registro (sólo UI)
        const s = siembras.value.find((x) => x.id === adicion.siembra) || {}
        ultimo.value = {
          siembraNombre: s.nombre || `Siembra ${adicion.siembra}`,
          especie: s.especie || '—',
          numeroOrganismos: adicion.numeroOrganismos,
          pesoPromedio: adicion.pesoPromedio,
          biomasaKg: biomasaKg.value,
          fecha: adicion.fecha,
        }

        // Reset mínimo conservando fecha
        const keepFecha = adicion.fecha
        limpiar()
        adicion.fecha = keepFecha

        alert('Organismos agregados exitosamente')
      } catch (e) {
        console.error('Error al agregar organismos', e)
        alert('Error al agregar organismos')
      } finally {
        loading.value = false
      }
    }

    function limpiar() {
      adicion.siembra = ''
      adicion.numeroOrganismos = null
      adicion.pesoPromedio = null
      // conserva la fecha por comodidad
    }

    onMounted(fetchSiembras)

    return {
      siembras,
      siembrasFiltradas,
      adicion,
      agregarOrganismos,
      limpiar,
      biomasaKg,
      formatNum,
      loading,
      ultimo,
      hoy,
    }
  },
}
</script>

<style scoped>
/* Sin estilos personalizados: todo se apoya en tu tema global.
   Sólo utilidades de layout mínimas ya provistas por el tema. */
</style>
