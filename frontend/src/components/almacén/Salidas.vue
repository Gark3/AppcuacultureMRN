<template>
  <section class="container">
    <!-- Card principal -->
    <form class="card" @submit.prevent="registrarSalida">
      <div class="card__header">
        <h2 class="card__title">Registro de Salidas de Productos</h2>
        <p class="card__sub">Descarga ítems del inventario y asigna un solicitante.</p>
      </div>

      <!-- Solicitante -->
      <div class="field">
        <label for="solicitante">Solicitante</label>
        <select
          id="solicitante"
          class="select"
          v-model="solicitanteId"
          :disabled="loadingUsuarios || usuariosDeMiAcuicola.length === 0"
          required
        >
          <option value="" disabled>Selecciona solicitante…</option>
          <option
            v-for="u in usuariosDeMiAcuicola"
            :key="u.id"
            :value="u.id"
          >
            {{ u.nombre }} ({{ u.correo || 'sin correo' }})
          </option>
        </select>
        <p v-if="loadingUsuarios" class="text-muted small">Cargando usuarios…</p>
      </div>

      <!-- Área de Uso -->
      <div class="field">
        <label for="area">Área de uso</label>
        <select id="area" class="select" v-model="salida.area" @change="cambioArea" required>
          <option value="">Seleccione un área</option>
          <option value="Estanque">Estanque</option>
          <option value="Laboratorio">Laboratorio</option>
          <option value="Almacén">Almacén</option>
        </select>
      </div>

      <!-- Selección de Siembra Activa (si área = Estanque) -->
      <div class="field" v-if="salida.area === 'Estanque'">
        <label for="siembra">Estanque (Siembra activa)</label>
        <select id="siembra" class="select" v-model.number="siembraSeleccionada" required>
          <option value="">Seleccione una siembra activa</option>
          <option
            v-for="siembra in siembras"
            :key="siembra.id_siembra"
            :value="siembra.id_siembra"
          >
            {{ siembra.estanque.nombre }} · {{ siembra.especie }} · {{ formatFecha(siembra.fecha) }}
          </option>
        </select>

        <div v-if="siembraSeleccionadaObjeto" class="text-muted small mt-2">
          <strong>Seleccionado:</strong>
          {{ siembraSeleccionadaObjeto.estanque.nombre }} ·
          {{ siembraSeleccionadaObjeto.especie }} ·
          {{ formatFecha(siembraSeleccionadaObjeto.fecha) }}
        </div>
      </div>

      <!-- Buscador de Producto -->
      <div class="field">
        <label for="producto">Buscar producto</label>
        <input
          id="producto"
          class="input"
          type="text"
          v-model="productoBusqueda"
          placeholder="Buscar por nombre o lote"
          @input="buscarProducto"
        />
        <ul v-if="productosDisponiblesFiltrados.length" class="listbox">
          <li
            v-for="item in productosDisponiblesFiltrados"
            :key="item.id_entrada_unitaria + '_' + item.lote"
            class="listbox__item"
            @click="seleccionarProducto(item)"
          >
            {{ item.nombre }} · Lote {{ item.lote }}
            <span class="text-muted">
              — Disponible:
              <template v-if="item.modo === 'kg'">{{ item.disponible }} Kg</template>
              <template v-else>{{ item.disponible }} Unidades</template>
            </span>
          </li>
        </ul>
      </div>

      <!-- Producto seleccionado -->
      <div class="card row-card" v-if="productoSeleccionado">
        <p class="mb-2">
          <strong>Producto:</strong> {{ productoSeleccionado.nombre }} · Lote {{ productoSeleccionado.lote }}
          <span class="text-muted">
            — Disponible:
            <template v-if="productoSeleccionado.modo === 'kg'">{{ productoSeleccionado.disponible }} Kg</template>
            <template v-else>{{ productoSeleccionado.disponible }} Unidades</template>
          </span>
        </p>
        <button type="button" class="btn btn--accent btn--sm" @click="agregarProducto">Agregar a la lista</button>
      </div>

      <!-- Tabla de productos agregados -->
      <div v-if="salida.productos.length">
        <h3 class="mt-3">Productos agregados</h3>
        <div class="table-wrap mt-1">
          <table class="table">
            <thead>
              <tr>
                <th style="width:120px;">ID Entrada</th>
                <th>Nombre</th>
                <th style="width:120px;">Lote</th>
                <th style="width:160px;">Disponibles</th>
                <th style="width:140px;">Cantidad</th>
                <th style="width:120px;" class="text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(prod, index) in salida.productos" :key="index">
                <td>{{ prod.id_entrada_unitaria }}</td>
                <td>{{ prod.nombre }}</td>
                <td>{{ prod.lote }}</td>
                <td>
                  {{ prod.disponible }}
                  {{ prod.modo === 'kg' ? 'Kg' : 'Unidades' }}
                </td>
                <td>
                  <input
                    class="input input-cell"
                    type="number"
                    v-model.number="prod.cantidad"
                    min="1"
                    @change="validarCantidad(index, prod.cantidad)"
                  />
                </td>
                <td class="text-right">
                  <button type="button" class="btn btn--outline btn--sm" @click="eliminarProducto(index)">
                    Eliminar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Submit -->
      <div class="mt-3">
        <button type="submit" class="btn btn--primary" :disabled="!salida.productos.length">
          Registrar salida
        </button>
      </div>
    </form>
  </section>
</template>

<script>
import axios from '@/services/axios';
export default {
  name: 'RegistroSalidas',
  data() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return {
      // contexto
      usuarioId: user?.usuario_id ?? null,
      acuicolaId: user?.acuicola ?? null,

      // formulario
      salida: {
        area: '',
        productos: [],
      },

      // solicitante (nuevo)
      solicitanteId: user?.usuario_id ?? null,
      usuarios: [],
      loadingUsuarios: false,

      // siembras / selección
      siembras: [],
      siembraSeleccionada: null,

      // inventario
      productoBusqueda: '',
      productoSeleccionado: null,
      entradasUnitarias: [],
      salidasUnitarias: [],
      productos: [],
    };
  },
  computed: {
    // Usuarios activos de mi acuícola
    usuariosDeMiAcuicola() {
      return (this.usuarios || []).filter(u =>
        (u.estado === 1 || u.estado === true) &&
        (this.acuicolaId == null || u.acuicola === this.acuicolaId)
      );
    },
    // Mapa id_producto -> nombre
    productMap() {
      const map = {};
      this.productos.forEach(p => {
        const pid = p.id ?? p.id_producto ?? p.pk;
        map[pid] = p.nombre;
      });
      return map;
    },
    // Stock por (id_entrada_unitaria, lote)
    productosConStock() {
      const map = {};
      this.entradasUnitarias.forEach(eu => {
        const idEU = eu.id ?? eu.id_entrada_unitaria;
        const prodId = typeof eu.producto === 'object' ? (eu.producto.id ?? eu.producto.id_producto) : eu.producto;
        const key = `${idEU}_${eu.lote}`;
        if (!map[key]) {
          map[key] = {
            id_entrada_unitaria: idEU,
            nombre: this.productMap[prodId] || 'SIN_NOMBRE',
            lote: eu.lote,
            modo: 'kg',
            sumKg: 0,
            sumUnidades: 0,
          };
        }
        map[key].sumKg += Number(eu.cantidad_kg) || 0;
        map[key].sumUnidades += Number(eu.unidades) || 0;
      });

      this.salidasUnitarias.forEach(su => {
        const idEU = su.producto; // así lo manejas en tu POST
        const key = `${idEU}_${su.lote}`;
        if (map[key]) {
          map[key].sumKg -= Number(su.cantidad_kg) || 0;
          map[key].sumUnidades -= Number(su.cantidad) || 0;
        }
      });

      // Solo lo disponible
      return Object.values(map)
        .map(rec => {
          if (rec.sumKg > 0) {
            return { id_entrada_unitaria: rec.id_entrada_unitaria, nombre: rec.nombre, lote: rec.lote, disponible: rec.sumKg, modo: 'kg' };
          } else if (rec.sumUnidades > 0) {
            return { id_entrada_unitaria: rec.id_entrada_unitaria, nombre: rec.nombre, lote: rec.lote, disponible: rec.sumUnidades, modo: 'unidades' };
          }
          return null;
        })
        .filter(Boolean);
    },
    productosDisponiblesFiltrados() {
      if (!this.productoBusqueda) return this.productosConStock;
      const term = this.productoBusqueda.toLowerCase();
      return this.productosConStock.filter(item =>
        (item.nombre && item.nombre.toLowerCase().includes(term)) ||
        (item.lote && item.lote.toLowerCase().includes(term)) ||
        (item.id_entrada_unitaria && String(item.id_entrada_unitaria).includes(term))
      );
    },
    siembraSeleccionadaObjeto() {
      return this.siembras.find(s => s.id_siembra === this.siembraSeleccionada);
    },
  },
  methods: {
    /* ---------- Carga de catálogos ---------- */
    async cargarUsuarios() {
      try {
        this.loadingUsuarios = true;
        const { data } = await axios.get('/usuario/');
        const arr = Array.isArray(data) ? data : (data.results || []);
        this.usuarios = arr.map(u => ({
          id: u.id ?? u.id_usuario ?? u.pk,
          nombre: u.nombre ?? u.nombre_completo ?? u.username ?? '',
          correo: u.correo ?? u.email ?? '',
          acuicola: u.acuicola ?? u.acuicola_id ?? null,
          estado: u.estado ?? 1,
        }));
      } catch (e) {
        console.error('No se pudieron cargar usuarios:', e);
        this.usuarios = [];
      } finally {
        this.loadingUsuarios = false;
      }
    },
    obtenerSiembras() {
      axios.get('/siembra/')
        .then(response => {
          const datos = Array.isArray(response.data) ? response.data : (response.data.results || []);
          this.siembras = datos.filter(s =>
            s.estado === 1 &&
            (typeof s.acuicola === 'object'
              ? s.acuicola.id_acuicola === this.acuicolaId
              : s.acuicola === this.acuicolaId)
          );
        })
        .catch(error => console.error('Error al obtener siembras:', error));
    },
    obtenerEntradasUnitarias() {
      axios.get('/entrada-unitaria/')
        .then(response => {
          this.entradasUnitarias = Array.isArray(response.data) ? response.data : (response.data.results || []);
        })
        .catch(error => console.error('Error al obtener entradas unitarias:', error));
    },
    obtenerSalidasUnitarias() {
      axios.get('/salida-unitaria/')
        .then(response => {
          this.salidasUnitarias = Array.isArray(response.data) ? response.data : (response.data.results || []);
        })
        .catch(error => console.error('Error al obtener salidas unitarias:', error));
    },
    obtenerProductos() {
      axios.get('/producto/')
        .then(response => {
          this.productos = Array.isArray(response.data) ? response.data : (response.data.results || []);
        })
        .catch(error => console.error('Error al obtener productos:', error));
    },

    /* ---------- Interacción ---------- */
    cambioArea() {
      if (this.salida.area !== 'Estanque') this.siembraSeleccionada = null;
    },
    buscarProducto() {}, // computed se encarga
    seleccionarProducto(item) {
      if (item.disponible > 0) {
        this.productoSeleccionado = { ...item };
        this.productoBusqueda = '';
      }
    },
    agregarProducto() {
      if (!this.productoSeleccionado) return;
      const existe = this.salida.productos.find(
        p => p.id_entrada_unitaria === this.productoSeleccionado.id_entrada_unitaria && p.lote === this.productoSeleccionado.lote
      );
      if (!existe) {
        this.salida.productos.push({
          id_entrada_unitaria: this.productoSeleccionado.id_entrada_unitaria,
          nombre: this.productoSeleccionado.nombre,
          lote: this.productoSeleccionado.lote,
          disponible: this.productoSeleccionado.disponible,
          modo: this.productoSeleccionado.modo,
          cantidad: 1,
        });
      }
      this.productoSeleccionado = null;
    },
    validarCantidad(index, cantidad) {
      const item = this.salida.productos[index];
      if (cantidad > item.disponible) {
        alert('La cantidad ingresada excede el stock disponible. Se ajustará al máximo permitido.');
        this.salida.productos[index].cantidad = item.disponible;
      } else if (cantidad < 1) {
        this.salida.productos[index].cantidad = 1;
      }
    },
    eliminarProducto(index) {
      this.salida.productos.splice(index, 1);
    },
    formatFecha(fecha) {
      const d = new Date(fecha);
      return d.toLocaleDateString();
    },

    /* ---------- Submit ---------- */
    registrarSalida() {
      if (!this.solicitanteId) {
        alert('Selecciona un solicitante.');
        return;
      }

      const salidaPayload = {
        solicitante: this.solicitanteId, // ✅ enviamos el ID del solicitante
        usuario: this.usuarioId,
        acuicola: this.acuicolaId,
        estado: 1,
      };

      axios.post('/salida/', salidaPayload)
        .then(salidaRes => {
          const salidaId = salidaRes.data.id_salida_producto || salidaRes.data.id;
          if (!salidaId) {
            alert('No se recibió el ID de la salida. Verifique la respuesta del servidor.');
            return;
          }

          const destino = this.salida.area === 'Estanque' ? 'Estanque' : this.salida.area;

          const salidaUnitariaPromises = this.salida.productos.map(producto => {
            if (producto.cantidad > producto.disponible) {
              alert(`La cantidad para ${producto.nombre} excede el stock disponible. Corrige antes de continuar.`);
              throw new Error('Cantidad excede stock disponible.');
            }
            const payloadUnitaria = {
              salida: salidaId,
              producto: producto.id_entrada_unitaria, // id de EntradaUnitaria
              lote: producto.lote,
              cantidad: producto.modo === 'kg' ? 0 : producto.cantidad,
              cantidad_kg: producto.modo === 'kg' ? producto.cantidad : 0,
              destino,
              usuario: this.usuarioId,
              acuicola: this.acuicolaId,
              estado: 1,
            };
            return axios.post('/salida-unitaria/', payloadUnitaria);
          });

          return Promise.all(salidaUnitariaPromises).then(respuestas => {
            if (this.salida.area === 'Estanque' && this.siembraSeleccionada) {
              const siembraId = this.siembraSeleccionada;
              const salidaEstanquePromises = respuestas.map(resp => {
                const salidaUnitariaId = resp.data.id_salida_unitaria || resp.data.id;
                return axios.post('/salida-estanque/', {
                  salidaunitaria: salidaUnitariaId,
                  siembra: siembraId,
                  usuario: this.usuarioId,
                  acuicola: this.acuicolaId,
                  estado: 1,
                });
              });
              return Promise.all(salidaEstanquePromises);
            }
          });
        })
        .then(() => {
          alert('¡Salida registrada con éxito!');
          this.salida = { area: '', productos: [] };
          this.siembraSeleccionada = null;
          // deja seleccionado al usuario logueado por comodidad
          // (si no quieres, comenta la siguiente línea)
          // this.solicitanteId = this.usuarioId;
        })
        .catch(err => {
          console.error('Error al registrar la salida:', err);
          alert('Ocurrió un error al registrar la salida.');
        });
    },
  },
  mounted() {
    this.cargarUsuarios();
    this.obtenerSiembras();
    this.obtenerEntradasUnitarias();
    this.obtenerSalidasUnitarias();
    this.obtenerProductos();
  },
};
</script>

<style scoped>
/* Usa tu tema global; sólo estilos mínimos para el buscador tipo listbox */
.listbox {
  list-style: none;
  margin: 6px 0 0;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  max-height: 220px;
  overflow: auto;
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
}
.listbox__item {
  padding: 10px 12px;
  cursor: pointer;
}
.listbox__item:hover {
  background: rgba(31,41,55,.06);
}
</style>
