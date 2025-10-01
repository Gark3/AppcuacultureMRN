<template>
  <!-- Encabezado + búsqueda -->
  <section class="card container">
    <div class="card__header">
      <h2 class="card__title">Inventario</h2>
      <p class="card__sub">Consulta el stock y el costo acumulado por producto.</p>
    </div>

    <div class="field">
      <label for="buscar">Buscar producto</label>
      <input
        id="buscar"
        v-model="filtro"
        class="input"
        type="text"
        placeholder="ID, nombre o rubro"
      />
    </div>
  </section>

  <!-- Tabla de inventario -->
  <section class="container">
    <div class="table-wrap">
      <table class="table table--zebra">
        <thead>
          <tr>
            <th style="width:80px;">ID</th>
            <th>Nombre</th>
            <th>Rubro</th>
            <th style="width:140px;">Cantidad</th>
            <th style="width:160px;">Costo acumulado</th>
            <th style="width:120px;" class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading && inventario.length === 0">
            <td colspan="6" class="text-center">Cargando inventario…</td>
          </tr>

          <tr v-for="item in paginated" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.nombre || '—' }}</td>
            <td>{{ item.rubro || '—' }}</td>
            <td>{{ formatNum(item.cantidad) }}</td>
            <td>$ {{ formatMoney(item.costoAcumulado) }}</td>
            <td class="text-right">
              <button class="btn btn--primary btn--sm" @click="verDetalles(item)">
                Ver
              </button>
            </td>
          </tr>

          <tr v-if="!loading && filtrados.length === 0">
            <td colspan="6" class="text-center">Sin resultados</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginación -->
    <div class="container" style="display:flex; align-items:center; justify-content:space-between; padding:10px 0;">
      <span class="text-muted small">
        Mostrando {{ startIdx + 1 }}–{{ endIdx }} de {{ filtrados.length }}
      </span>
      <div style="display:flex; gap:8px;">
        <button class="btn btn--outline btn--sm" :disabled="page === 1" @click="page--">Anterior</button>
        <button class="btn btn--outline btn--sm" :disabled="endIdx >= filtrados.length" @click="page++">Siguiente</button>
      </div>
    </div>
  </section>

  <!-- Modal: detalle por producto -->
  <div v-if="showModal" class="overlay" @click.self="cerrarModal">
    <div class="card modal-card">
      <div class="card__header" style="display:flex; align-items:center; justify-content:space-between;">
        <div>
          <h3 class="card__title">Detalle de entradas</h3>
          <p class="card__sub">
            <strong>Producto:</strong> {{ activo?.nombre }} (ID: {{ activo?.id }})
          </p>
        </div>
        <button class="btn btn--ghost btn--sm" @click="cerrarModal">✕</button>
      </div>

      <div class="table-wrap" style="max-height:60vh;">
        <table class="table">
          <thead>
            <tr>
              <th style="width:110px;">Fecha</th>
              <th>Proveedor</th>
              <th style="width:120px;">Lote</th>
              <th style="width:110px;">Kg</th>
              <th style="width:110px;">Unidades</th>
              <th style="width:120px;">Costo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingDetalle">
              <td colspan="6" class="text-center">Cargando detalle…</td>
            </tr>
            <tr v-else-if="detalle.length === 0">
              <td colspan="6" class="text-center">No hay entradas para este producto.</td>
            </tr>
            <tr v-else v-for="d in detalle" :key="d.id">
              <td>{{ d.fecha }}</td>
              <td>{{ d.proveedor || '—' }}</td>
              <td>{{ d.lote || '—' }}</td>
              <td>{{ formatNum(d.kg) }}</td>
              <td>{{ formatNum(d.unidades) }}</td>
              <td>$ {{ formatMoney(d.costo) }}</td>
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
import axios from '@/services/axios';
import { ref, computed, onMounted } from 'vue';

/* ===== ENDPOINTS (ajústalos a tus rutas reales) ===== */
const ENDPOINTS = {
  productos: '/producto/',
  entradaUnitaria: '/entradaunitaria/',                          // detalle (tiene producto y entrada)
  entradas: '/entrada/',                                         // para obtener proveedor por entrada
  proveedores: '/proveedor/',                                    // catálogo de proveedores
};

/* ===== Mappers para alinear con tus serializers ===== */
function mapProducto(apiObj) {
  return {
    id: apiObj.id ?? apiObj.id_producto ?? apiObj.pk,
    nombre: apiObj.nombre ?? '',
    rubro: apiObj.rubro ?? '',
    presentacion: apiObj.presentacion ?? '',
  };
}

function mapEntradaUnitaria(apiObj) {
  return {
    id: apiObj.id ?? apiObj.id_entrada_unitaria ?? apiObj.pk,
    fecha: (apiObj.fecha || '').toString().slice(0, 10),
    producto: apiObj.producto ?? apiObj.producto_id ?? apiObj.id_producto,
    entrada: apiObj.entrada ?? apiObj.entrada_id ?? apiObj.id_entrada,
    cantidad_kg: Number(apiObj.cantidad_kg ?? apiObj.kg ?? 0),
    unidades: Number(apiObj.unidades ?? apiObj.cantidad ?? 0),
    costo: Number(apiObj.costo ?? 0),
    lote: apiObj.lote ?? '',
    acuicola: apiObj.acuicola ?? apiObj.acuicola_id ?? null,
  };
}

function mapEntrada(apiObj) {
  return {
    id: apiObj.id ?? apiObj.id_entrada ?? apiObj.pk,
    proveedor: apiObj.proveedor ?? apiObj.proveedor_id ?? null,
  };
}

function mapProveedor(apiObj) {
  return {
    id: apiObj.id ?? apiObj.id_proveedor ?? apiObj.pk,
    nombre: apiObj.nombre ?? apiObj.razon_social ?? '',
  };
}

export default {
  name: 'Inventario',
  setup() {
    const filtro = ref('');
    const loading = ref(false);

    const inventario = ref([]);  // [{id, nombre, rubro, cantidad, costoAcumulado}]
    const productosById = ref({});
    const unitByProducto = ref({}); // productoId -> [entradaunitaria]

    // modal
    const showModal = ref(false);
    const activo = ref(null);
    const detalle = ref([]);
    const loadingDetalle = ref(false);

    // paginación
    const page = ref(1);
    const pageSize = ref(10);

    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const acuicolaId = user?.acuicola ?? null;

    const filtrados = computed(() => {
      const q = filtro.value.trim().toLowerCase();
      if (!q) return inventario.value;
      return inventario.value.filter((p) =>
        [p.id, p.nombre, p.rubro]
          .map((v) => String(v ?? '').toLowerCase())
          .some((s) => s.includes(q))
      );
    });

    const startIdx = computed(() => (page.value - 1) * pageSize.value);
    const endIdx = computed(() =>
      Math.min(startIdx.value + pageSize.value, filtrados.value.length)
    );
    const paginated = computed(() =>
      filtrados.value.slice(startIdx.value, endIdx.value)
    );

    function formatNum(n) {
      const x = Number(n || 0);
      return Number.isFinite(x) ? x.toLocaleString() : '0';
    }
    function formatMoney(n) {
      const x = Number(n || 0);
      return Number.isFinite(x) ? x.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00';
    }

    async function cargarInventario() {
      loading.value = true;
      try {
        // 1) productos, entradas unitarias, entradas y proveedores
        const [prodRes, euRes, entRes, provRes] = await Promise.all([
          axios.get(ENDPOINTS.productos),
          axios.get(ENDPOINTS.entradaUnitaria),
          axios.get(ENDPOINTS.entradas),
          axios.get(ENDPOINTS.proveedores),
        ]);

        const productos = (Array.isArray(prodRes.data) ? prodRes.data : (prodRes.data.results || [])).map(mapProducto);
        const unitarias = (Array.isArray(euRes.data) ? euRes.data : (euRes.data.results || [])).map(mapEntradaUnitaria);
        const entradas = (Array.isArray(entRes.data) ? entRes.data : (entRes.data.results || [])).map(mapEntrada);
        const proveedores = (Array.isArray(provRes.data) ? provRes.data : (provRes.data.results || [])).map(mapProveedor);

        // Diccionarios
        productosById.value = Object.fromEntries(productos.map(p => [p.id, p]));
        const entradaToProveedor = Object.fromEntries(entradas.map(e => [e.id, e.proveedor]));
        const proveedorToNombre = Object.fromEntries(proveedores.map(p => [p.id, p.nombre]));

        // 2) filtra por acuícola si viene en la unidad
        const unitariasFiltradas = unitarias.filter(u => (acuicolaId == null) || (u.acuicola == null) || (u.acuicola === acuicolaId));

        // 3) agrupa por producto
        const acc = {};
        const bucket = {};
        for (const u of unitariasFiltradas) {
          if (!u.producto) continue;
          if (!acc[u.producto]) acc[u.producto] = { cantidad: 0, costo: 0 };
          if (!bucket[u.producto]) bucket[u.producto] = [];
          acc[u.producto].cantidad += Number.isFinite(u.unidades) ? u.unidades : 0;
          acc[u.producto].costo += Number.isFinite(u.costo) ? u.costo : 0;

          // guarda fila detallada (con proveedor resuelto)
          bucket[u.producto].push({
            id: u.id,
            fecha: u.fecha,
            proveedor: proveedorToNombre[entradaToProveedor[u.entrada]] || '',
            lote: u.lote,
            kg: u.cantidad_kg,
            unidades: u.unidades,
            costo: u.costo,
          });
        }

        unitByProducto.value = bucket;

        // 4) arma la tabla final (solo productos con movimiento)
        inventario.value = Object.keys(acc).map(pid => {
          const p = productosById.value[pid] || { id: pid, nombre: '', rubro: '' };
          return {
            id: p.id,
            nombre: p.nombre,
            rubro: p.rubro,
            cantidad: acc[pid].cantidad,
            costoAcumulado: acc[pid].costo,
          };
        }).sort((a,b) => String(a.nombre).localeCompare(String(b.nombre)));
      } catch (e) {
        console.error('Error al cargar inventario:', e);
        inventario.value = [];
      } finally {
        loading.value = false;
      }
    }

    function verDetalles(item) {
      activo.value = item;
      detalle.value = unitByProducto.value[item.id] || [];
      showModal.value = true;
    }

    function cerrarModal() {
      showModal.value = false;
      activo.value = null;
      detalle.value = [];
    }

    onMounted(cargarInventario);

    return {
      // estado
      filtro, inventario, loading,
      showModal, activo, detalle, loadingDetalle,
      // paginación y filtrado
      filtrados, paginated, startIdx, endIdx, page, pageSize,
      // acciones
      verDetalles, cerrarModal,
      // utils
      formatNum, formatMoney,
    };
  },
};
</script>

<style scoped>
/* Modal: reutiliza .overlay global; solo le damos ancho a la card */
.modal-card { max-width: 1100px; width: 100%; }
@media (max-width: 768px) { .modal-card { max-width: 95vw; } }
</style>
