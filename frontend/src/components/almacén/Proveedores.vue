<template>
  <!-- Encabezado + buscador -->
  <section class="card container">
    <div class="card__header">
      <h2 class="card__title">Proveedores</h2>
      <p class="card__sub">Consulta tus proveedores y revisa el detalle de sus entregas.</p>
    </div>

    <div class="field">
      <label for="buscar">Buscar proveedor</label>
      <input
        id="buscar"
        v-model="search"
        class="input"
        type="text"
        placeholder="Nombre, correo, teléfono o ID"
        @input="onSearch"
      />
    </div>
  </section>

  <!-- Tabla de proveedores -->
  <section class="container">
    <div class="table-wrap">
      <table class="table table--zebra">
        <thead>
          <tr>
            <th style="width:80px;">ID</th>
            <th>Nombre</th>
            <th>Correo</th>
            <th style="width:160px;">Teléfono</th>
            <th style="width:120px;" class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading && proveedores.length === 0">
            <td colspan="5" class="text-center">Cargando proveedores…</td>
          </tr>

          <tr v-for="p in paginated" :key="p.id">
            <td>{{ p.id }}</td>
            <td>{{ p.nombre || '—' }}</td>
            <td>{{ p.correo || '—' }}</td>
            <td>{{ p.telefono || '—' }}</td>
            <td class="text-right">
              <button class="btn btn--primary btn--sm" @click="abrirModal(p)">
                Ver
              </button>
            </td>
          </tr>

          <tr v-if="!loading && proveedoresFiltrados.length === 0">
            <td colspan="5" class="text-center">Sin resultados</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginación -->
    <div class="container" style="display:flex; align-items:center; justify-content:space-between; padding:10px 0;">
      <span class="text-muted small">
        Mostrando {{ startIdx + 1 }}–{{ endIdx }} de {{ proveedoresFiltrados.length }}
      </span>
      <div style="display:flex; gap:8px;">
        <button class="btn btn--outline btn--sm" :disabled="page === 1" @click="page--">Anterior</button>
        <button class="btn btn--outline btn--sm" :disabled="endIdx >= proveedoresFiltrados.length" @click="page++">Siguiente</button>
      </div>
    </div>
  </section>

  <!-- Modal: detalle de entradas unitarias -->
  <div v-if="showModal" class="overlay" @click.self="cerrarModal">
    <div class="card modal-card">
      <div class="card__header" style="display:flex; align-items:center; justify-content:space-between;">
        <div>
          <h3 class="card__title">Detalle de entregas</h3>
          <p class="card__sub">
            <strong>Proveedor:</strong> {{ proveedorActivo?.nombre }} (ID: {{ proveedorActivo?.id }})
          </p>
        </div>
        <button class="btn btn--ghost btn--sm" @click="cerrarModal">✕</button>
      </div>

      <div class="table-wrap" style="max-height:60vh;">
        <table class="table">
          <thead>
            <tr>
              <th style="width:80px;">ID</th>
              <th style="width:110px;">Fecha</th>
              <th>Producto</th>
              <th style="width:110px;">Kg</th>
              <th style="width:110px;">Unidades</th>
              <th style="width:110px;">Costo</th>
              <th style="width:120px;">Lote</th>
              <th style="width:160px;">Presentación</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingEntregas">
              <td colspan="8" class="text-center">Cargando entregas…</td>
            </tr>

            <tr v-else-if="entregas.length === 0">
              <td colspan="8" class="text-center">No hay entregas registradas para este proveedor.</td>
            </tr>

            <tr v-else v-for="e in entregas" :key="e.id">
              <td>{{ e.id }}</td>
              <td>{{ e.fecha }}</td>
              <td>{{ e.producto || '—' }}</td>
              <td>{{ e.cantidad_kg ?? '—' }}</td>
              <td>{{ e.unidades ?? '—' }}</td>
              <td>{{ e.costo ?? '—' }}</td>
              <td>{{ e.lote || '—' }}</td>
              <td>{{ e.presentacion || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div style="display:flex; justify-content:flex-end; margin-top:12px;">
        <button class="btn btn--outline btn--sm" @click="cerrarModal">Cerrar</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/services/axios'; // usa tu wrapper como en "Siembras Activas"
import { ref, computed, onMounted } from 'vue';

/* ====== ENDPOINTS (ajústalos si tus rutas difieren) ====== */
const ENDPOINTS = {
  proveedores: '/proveedor/',                                // lista de proveedores
  entradasPorProveedor: (provId) => `/entrada/?proveedor=${provId}`,         // <--- ajusta si es distinto
  entradaUnitariaPorEntrada: (entradaId) => `/entradaunitaria/?entrada=${entradaId}`, // <--- ajusta si es distinto
  entradaUnitariaPorLista: (idsCSV) => `/entradaunitaria/?entrada__in=${idsCSV}`, // si tu API soporta __in
  productos: '/producto/',                                   // catálogo para nombre/presentación
};

/* ====== Mapers para alinear los campos del API con la UI ====== */
function mapProveedor(apiObj) {
  return {
    id: apiObj.id ?? apiObj.id_proveedor ?? apiObj.pk,
    nombre: apiObj.nombre ?? apiObj.razon_social ?? '',
    correo: apiObj.correo ?? apiObj.email ?? '',
    telefono: apiObj.telefono ?? apiObj.celular ?? '',
  };
}

function mapEntrada(apiObj) {
  const guessKey = Object.keys(apiObj || {}).find(k => /^id(_entrada)?$/i.test(k));
  const id =
    apiObj?.id ??
    apiObj?.id_entrada ??
    apiObj?.idEntrada ??
    apiObj?.identrada ??
    (guessKey ? apiObj[guessKey] : undefined) ??
    apiObj?.pk;

  return { id };
}


function mapEntradaUnitaria(apiObj, productosById = {}) {
  const prodId = apiObj.producto ?? apiObj.producto_id ?? apiObj.id_producto;
  const prod = productosById[prodId] || {};
  return {
    id: apiObj.id ?? apiObj.id_entrada_unitaria ?? apiObj.pk,
    fecha: (apiObj.fecha || '').toString().slice(0, 10),
    producto: apiObj.producto_nombre ?? prod.nombre ?? prodId ?? '',
    presentacion: apiObj.presentacion ?? prod.presentacion ?? '',
    cantidad_kg: apiObj.cantidad_kg ?? apiObj.kg ?? '',
    unidades: apiObj.unidades ?? apiObj.cantidad ?? '',
    costo: apiObj.costo ?? '',
    lote: apiObj.lote ?? '',
  };
}

export default {
  name: 'ListaProveedores',
  setup() {
    const proveedores = ref([]);
    const loading = ref(false);
    const error = ref(null);

    const search = ref('');
    const page = ref(1);
    const pageSize = ref(10);

    const showModal = ref(false);
    const proveedorActivo = ref(null);
    const entregas = ref([]);
    const loadingEntregas = ref(false);

    const proveedoresFiltrados = computed(() => {
      const q = search.value.trim().toLowerCase();
      if (!q) return proveedores.value;
      return proveedores.value.filter((p) =>
        [p.nombre, p.correo, p.telefono, String(p.id)]
          .filter(Boolean)
          .some((v) => v.toString().toLowerCase().includes(q))
      );
    });

    const startIdx = computed(() => (page.value - 1) * pageSize.value);
    const endIdx = computed(() =>
      Math.min(startIdx.value + pageSize.value, proveedoresFiltrados.value.length)
    );
    const paginated = computed(() =>
      proveedoresFiltrados.value.slice(startIdx.value, endIdx.value)
    );

    function onSearch() { page.value = 1; }

    async function cargarProveedores() {
      try {
        loading.value = true;
        error.value = null;
        const { data } = await axios.get(ENDPOINTS.proveedores);
        const arr = Array.isArray(data) ? data : (data.results || []);
        proveedores.value = arr.map(mapProveedor);
      } catch (e) {
        error.value = 'No se pudieron cargar los proveedores';
        console.error(e);
      } finally {
        loading.value = false;
      }
    }

    async function abrirModal(proveedor) {
      proveedorActivo.value = proveedor;
      showModal.value = true;
      entregas.value = [];
      loadingEntregas.value = true;

      try {
        // 1) Traer entradas del proveedor
        const { data: entradasRes } = await axios.get(
          ENDPOINTS.entradasPorProveedor(proveedor.id)
        );
        const entradasArr = Array.isArray(entradasRes)
          ? entradasRes
          : (entradasRes.results || []);

        // ids robustos
        const ids = entradasArr.map(mapEntrada).map(e => e.id).filter(id => id != null);

        // Si no hay ids, no consultamos detalle
        if (ids.length === 0) {
          entregas.value = [];
          return;
        }

        // 2) Catálogo de productos (para nombre/presentación)
        const { data: prodsRes } = await axios.get(ENDPOINTS.productos);
        const prodsArr = Array.isArray(prodsRes) ? prodsRes : (prodsRes.results || []);
        const productosById = {};
        for (const p of prodsArr) {
          const pid = p.id ?? p.id_producto ?? p.pk;
          productosById[pid] = { nombre: p.nombre, presentacion: p.presentacion };
        }

        // 3) Traer entradas unitarias una por una (sin __in)
        const requests = ids.map(id =>
          axios.get(ENDPOINTS.entradaUnitariaPorEntrada(id))
        );

        const results = await Promise.allSettled(requests);

        let unitArr = [];
        for (const r of results) {
          if (r.status === 'fulfilled') {
            const d = r.value.data;
            unitArr = unitArr.concat(Array.isArray(d) ? d : (d.results || []));
          } else {
            // Ignora 404 individuales para alguna entrada
            // console.warn('Fallo al traer detalle de una entrada:', r.reason);
          }
        }

        // 4) Mapear a la UI
        entregas.value = unitArr.map(u => mapEntradaUnitaria(u, productosById));
      } catch (e) {
        console.error('Error al cargar entregas:', e);
        entregas.value = [];
      } finally {
        loadingEntregas.value = false;
      }
    }

    function cerrarModal() {
      showModal.value = false;
      proveedorActivo.value = null;
      entregas.value = [];
    }

    onMounted(cargarProveedores);

    return {
      proveedores, loading, error,
      search, page, pageSize,
      proveedoresFiltrados, paginated, startIdx, endIdx,
      showModal, proveedorActivo, entregas, loadingEntregas,
      onSearch, abrirModal, cerrarModal,
    };
  },
};
</script>

<style scoped>
/* Usamos tu overlay global (.overlay) y componemos el contenido con .card */
.modal-card {
  max-width: 1000px;
  width: 100%;
}
@media (max-width: 768px) {
  .modal-card { max-width: 95vw; }
}
</style>
