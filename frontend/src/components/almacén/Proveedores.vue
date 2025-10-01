<template>
  <div class="p-4 space-y-4">
    <h1 class="text-xl font-semibold">Proveedores</h1>

    <!-- Barra de búsqueda -->
    <div class="flex items-center gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por nombre, correo o teléfono…"
        class="border rounded px-3 py-2 w-full"
        @input="onSearch"
      />
    </div>

    <!-- Tabla de proveedores -->
    <div class="border rounded overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-100">
          <tr>
            <th class="text-left px-3 py-2">ID</th>
            <th class="text-left px-3 py-2">Nombre</th>
            <th class="text-left px-3 py-2">Correo</th>
            <th class="text-left px-3 py-2">Teléfono</th>
            <th class="text-left px-3 py-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading && proveedores.length === 0">
            <td colspan="5" class="px-3 py-6 text-center">Cargando proveedores…</td>
          </tr>

          <tr
            v-for="p in paginated"
            :key="p.id"
            class="border-t"
          >
            <td class="px-3 py-2">{{ p.id }}</td>
            <td class="px-3 py-2">{{ p.nombre }}</td>
            <td class="px-3 py-2">{{ p.correo }}</td>
            <td class="px-3 py-2">{{ p.telefono }}</td>
            <td class="px-3 py-2">
              <button
                class="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
                @click="abrirModal(p)"
              >
                Ver
              </button>
            </td>
          </tr>

          <tr v-if="!loading && proveedoresFiltrados.length === 0">
            <td colspan="5" class="px-3 py-6 text-center">Sin resultados</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginación -->
    <div class="flex items-center justify-between">
      <div class="text-sm text-gray-600">
        Mostrando {{ startIdx + 1 }}–{{ endIdx }} de {{ proveedoresFiltrados.length }}
      </div>
      <div class="flex gap-2">
        <button
          class="px-3 py-1 rounded border"
          :disabled="page === 1"
          @click="page--"
        >
          Anterior
        </button>
        <button
          class="px-3 py-1 rounded border"
          :disabled="endIdx >= proveedoresFiltrados.length"
          @click="page++"
        >
          Siguiente
        </button>
      </div>
    </div>

    <!-- Modal de entregas -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg w-full max-w-3xl shadow-lg">
        <div class="flex items-center justify-between px-4 py-3 border-b">
          <h2 class="font-semibold">
            Entregas de: <span class="font-bold">{{ proveedorActivo?.nombre }}</span>
          </h2>
          <button class="text-gray-600 hover:text-black" @click="cerrarModal">✕</button>
        </div>

        <div class="p-4 max-h-[70vh] overflow-y-auto">
          <div v-if="loadingEntregas" class="py-6 text-center">Cargando entregas…</div>

          <template v-else>
            <div v-if="entregas.length === 0" class="text-center text-gray-600 py-8">
              No hay entregas registradas para este proveedor.
            </div>

            <table v-else class="min-w-full text-sm border rounded">
              <thead class="bg-gray-100">
                <tr>
                  <th class="text-left px-3 py-2">ID</th>
                  <th class="text-left px-3 py-2">Fecha</th>
                  <th class="text-left px-3 py-2">Producto</th>
                  <th class="text-left px-3 py-2">Descripción</th>
                  <th class="text-left px-3 py-2">Cantidad</th>
                  <th class="text-left px-3 py-2">Presentación</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in entregas" :key="e.id" class="border-t">
                  <td class="px-3 py-2">{{ e.id }}</td>
                  <td class="px-3 py-2">{{ e.fecha }}</td>
                  <td class="px-3 py-2">{{ e.producto }}</td>
                  <td class="px-3 py-2">{{ e.descripcion }}</td>
                  <td class="px-3 py-2">{{ e.cantidad }}</td>
                  <td class="px-3 py-2">{{ e.presentacion }}</td>
                </tr>
              </tbody>
            </table>
          </template>
        </div>

        <div class="px-4 py-3 border-t flex justify-end">
          <button class="px-3 py-1 rounded border" @click="cerrarModal">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { ref, computed, onMounted } from "vue";

/** ========= CONFIG =========
 * Ajusta los endpoints a tus rutas DRF:
 *  - LISTA PROVEEDORES: GET    /proveedor/
 *  - ENTREGAS POR PROVEEDOR: GET /entrada/?proveedor=<id>
 *
 * Si tus nombres de campos difieren, ajusta
 * mapProveedor() y mapEntrega() debajo.
 */
const ENDPOINTS = {
  proveedores: "/proveedor/",
  entregasPorProveedor: (id) => `/entrada/?proveedor=${id}`,
};

// Convierte el objeto del API en el que la UI espera
function mapProveedor(apiObj) {
  return {
    id: apiObj.id ?? apiObj.id_proveedor ?? apiObj.pk,
    nombre: apiObj.nombre ?? "",
    correo: apiObj.correo ?? "",
    telefono: apiObj.telefono ?? "",
  };
}

// Mapea una "entrada" (entrega) con campos comunes.
// Ajusta según tu serializer (Entrada/EntradaUnitaria).
function mapEntrega(apiObj) {
  return {
    id: apiObj.id ?? apiObj.id_entrada ?? apiObj.pk,
    fecha: (apiObj.fecha || "").toString().slice(0, 10),
    producto:
      apiObj.producto_nombre ??
      apiObj.producto?.nombre ??
      apiObj.producto ??
      "",
    descripcion:
      apiObj.descripcion ??
      apiObj.detalle ??
      apiObj.nota ??
      "",
    cantidad: apiObj.cantidad ?? apiObj.cant ?? apiObj.unidades ?? "",
    presentacion:
      apiObj.presentacion ??
      apiObj.producto?.presentacion ??
      "",
  };
}

export default {
  name: "ListaProveedores",
  setup() {
    const proveedores = ref([]);
    const loading = ref(false);
    const error = ref(null);

    const search = ref("");
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

    function onSearch() {
      page.value = 1;
    }

    async function cargarProveedores() {
      try {
        loading.value = true;
        error.value = null;
        const { data } = await axios.get(ENDPOINTS.proveedores);
        // Si tu ViewSet usa paginación DRF, data.results es el arreglo
        const arr = Array.isArray(data) ? data : (data.results || []);
        proveedores.value = arr.map(mapProveedor);
      } catch (e) {
        error.value = "No se pudieron cargar los proveedores";
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
        const { data } = await axios.get(
          ENDPOINTS.entregasPorProveedor(proveedor.id)
        );
        const arr = Array.isArray(data) ? data : (data.results || []);
        entregas.value = arr.map(mapEntrega);
      } catch (e) {
        console.error("Error al cargar entregas:", e);
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
      // estado
      proveedores,
      loading,
      error,
      search,
      page,
      pageSize,
      proveedoresFiltrados,
      paginated,
      startIdx,
      endIdx,
      // modal
      showModal,
      proveedorActivo,
      entregas,
      loadingEntregas,
      // acciones
      onSearch,
      abrirModal,
      cerrarModal,
    };
  },
};
</script>

<style scoped>
.proveedores {
  font-family: Arial, sans-serif;
  max-width: auto;
  margin: 0 auto;
  padding: 20px;
  background: #f9f9f9;
  border: 1px solid #ccc;
  border-radius: 10px;
}

h1 {
  text-align: center;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.tabla-proveedores {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.tabla-proveedores th,
.tabla-proveedores td {
  border: 1px solid #ccc;
  padding: 10px;
  text-align: left;
}

.tabla-proveedores th {
  background-color: #f0f0f0;
}

.tabla-productos {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.tabla-productos th,
.tabla-productos td {
  border: 1px solid #ccc;
  padding: 10px;
  text-align: left;
}

.tabla-productos th {
  background-color: #f0f0f0;
}

button {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 8px 12px;
    font-size: 14px;
    cursor: pointer;
    border-radius: 5px;
  }
  
  button:hover {
    background-color: #218838;
  }

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-contenido {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  max-width: auto;
  width: 100%;
}
</style>
