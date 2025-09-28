<template>
  <div class="registro-salidas">
    <h1>Registro de Salidas de Productos</h1>
    <form @submit.prevent="registrarSalida">
      <!-- Solicitante -->
      <div class="form-group">
        <label for="solicitante">Solicitante</label>
        <input
          type="number"
          id="solicitante"
          v-model.number="salida.solicitante"
          placeholder="Ingrese ID del solicitante"
          required
        />
      </div>

      <!-- Área de Uso -->
      <div class="form-group">
        <label for="area">Área de Uso</label>
        <select id="area" v-model="salida.area" @change="cambioArea" required>
          <option value="">Seleccione un área</option>
          <option value="Estanque">Estanque</option>
          <option value="Laboratorio">Laboratorio</option>
          <option value="Almacén">Almacén</option>
        </select>
      </div>

      <!-- Selección de Siembra Activa para área "Estanque" -->
      <div class="form-group" v-if="salida.area === 'Estanque'">
        <label for="siembra">Seleccione el Estanque (Siembra Activa)</label>
        <select id="siembra" v-model.number="siembraSeleccionada" required>
          <option value="">Seleccione una siembra activa</option>
          <option 
            v-for="siembra in siembras" 
            :key="siembra.id_siembra" 
            :value="siembra.id_siembra"
          >
            {{ siembra.estanque.nombre }} - {{ siembra.especie }} - {{ formatFecha(siembra.fecha) }}
          </option>
        </select>
        <div v-if="siembraSeleccionadaObjeto" class="selected-item">
          <p>
            <strong>Estanque seleccionado:</strong>
            {{ siembraSeleccionadaObjeto.estanque.nombre }} - {{ siembraSeleccionadaObjeto.especie }} - {{ formatFecha(siembraSeleccionadaObjeto.fecha) }}
          </p>
        </div>
      </div>

      <!-- Buscador y selección de Producto (basado en EntradaUnitaria) -->
      <div class="form-group">
        <label for="producto">Buscar Producto</label>
        <input
          type="text"
          id="producto"
          v-model="productoBusqueda"
          placeholder="Buscar por nombre o lote"
          @input="buscarProducto"
        />
        <ul v-if="productosDisponiblesFiltrados.length" class="autocomplete">
          <li
            v-for="item in productosDisponiblesFiltrados"
            :key="item.id_entrada_unitaria + '_' + item.lote"
            @click="seleccionarProducto(item)"
          >
            {{ item.nombre }} - {{ item.lote }}
            <span v-if="item.modo === 'kg'">
              (Disponible: {{ item.disponible }} Kg)
            </span>
            <span v-else>
              (Disponible: {{ item.disponible }} Unidades)
            </span>
          </li>
        </ul>
      </div>

      <!-- Visualización del Producto seleccionado -->
      <div class="info-seleccion" v-if="productoSeleccionado">
        <p class="selected-product">
          <strong>Producto seleccionado:</strong>
          {{ productoSeleccionado.nombre }} - {{ productoSeleccionado.lote }}
          <span v-if="productoSeleccionado.modo === 'kg'">
            (Disponible: {{ productoSeleccionado.disponible }} Kg)
          </span>
          <span v-else>
            (Disponible: {{ productoSeleccionado.disponible }} Unidades)
          </span>
        </p>
        <button type="button" class="btn-agregar" @click="agregarProducto">
          Agregar a la lista
        </button>
      </div>

      <!-- Lista de productos agregados -->
      <div class="lista-productos" v-if="salida.productos.length">
        <h2>Productos Agregados</h2>
        <table class="productos-table">
          <thead>
            <tr>
              <th>ID Entrada</th>
              <th>Nombre</th>
              <th>Lote</th>
              <th>Disponibles</th>
              <th>Cantidad</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(prod, index) in salida.productos" :key="index">
              <td>{{ prod.id_entrada_unitaria }}</td>
              <td>{{ prod.nombre }}</td>
              <td>{{ prod.lote }}</td>
              <td>{{ prod.disponible }} {{ prod.modo === 'kg' ? 'Kg' : 'Unidades' }}</td>
              <td>
                <input
                  type="number"
                  v-model.number="prod.cantidad"
                  min="1"
                  @change="validarCantidad(index, prod.cantidad)"
                />
              </td>
              <td>
                <button type="button" class="btn-eliminar" @click="eliminarProducto(index)">
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Botón para registrar la salida -->
      <button type="submit" class="btn-registrar" :disabled="!salida.productos.length">
        Registrar Salida
      </button>
    </form>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "RegistroSalidas",
  data() {
    return {
      usuarioId: 1,
      acuicolaId: 1,
      salida: {
        solicitante: "",
        area: "",
        productos: []
      },
      siembras: [],
      siembraSeleccionada: null,
      productoBusqueda: "",
      // Producto seleccionado se basará en la entrada unitaria
      productoSeleccionado: null,
      entradasUnitarias: [],
      salidasUnitarias: [],
      // Nuevo arreglo para obtener la lista de todos los productos
      productos: []
    };
  },
  computed: {
    // Mapping de productos: clave = id_producto y valor = nombre
    productMap() {
      const map = {};
      this.productos.forEach(p => {
        map[p.id_producto] = p.nombre;
      });
      return map;
    },
    // Se construye la lista de stock a partir de las entradas unitarias
    productosConStock() {
      const map = {};
      this.entradasUnitarias.forEach(e => {
        // Extraer el id del producto: si e.producto es un objeto, usar su id; sino, usar e.producto directamente
        const prodId = typeof e.producto === "object" ? e.producto.id_producto : e.producto;
        const key = e.id_entrada_unitaria + "_" + e.lote;
        if (!map[key]) {
          map[key] = {
            id_entrada_unitaria: e.id_entrada_unitaria,
            nombre: this.productMap[prodId] || "SIN_NOMBRE",
            lote: e.lote,
            // Se asume modo "kg" (ajusta si en tu API se envía otro valor)
            modo: "kg",
            sumKg: 0,
            sumUnidades: 0
          };
        }
        map[key].sumKg += Number(e.cantidad_kg) || 0;
        map[key].sumUnidades += Number(e.unidades) || 0;
      });
      this.salidasUnitarias.forEach(s => {
        // Asumimos que en SalidaUnitaria se guarda el id de la entrada unitaria en el campo "producto"
        // y se combina con el lote para construir la clave.
        const key = s.producto + "_" + s.lote;
        if (map[key]) {
          map[key].sumKg -= Number(s.cantidad_kg) || 0;
          map[key].sumUnidades -= Number(s.cantidad) || 0;
        }
      });
      const result = [];
      for (let key in map) {
        const rec = map[key];
        if (rec.sumKg > 0) {
          result.push({
            id_entrada_unitaria: rec.id_entrada_unitaria,
            nombre: rec.nombre,
            lote: rec.lote,
            disponible: rec.sumKg,
            modo: "kg"
          });
        } else if (rec.sumUnidades > 0) {
          result.push({
            id_entrada_unitaria: rec.id_entrada_unitaria,
            nombre: rec.nombre,
            lote: rec.lote,
            disponible: rec.sumUnidades,
            modo: "unidades"
          });
        }
      }
      return result.filter(item => item.disponible > 0);
    },
    productosDisponiblesFiltrados() {
      if (!this.productoBusqueda) return this.productosConStock;
      const term = this.productoBusqueda.toLowerCase();
      return this.productosConStock.filter(item =>
        (item.nombre && item.nombre.toLowerCase().includes(term)) ||
        (item.lote && item.lote.toLowerCase().includes(term)) ||
        (item.id_entrada_unitaria && item.id_entrada_unitaria.toString().includes(term))
      );
    },
    siembraSeleccionadaObjeto() {
      return this.siembras.find(s => s.id_siembra === this.siembraSeleccionada);
    }
  },
  methods: {
    cambioArea() {
      if (this.salida.area !== "Estanque") {
        this.siembraSeleccionada = null;
      }
    },
    obtenerSiembras() {
      axios
        .get("/siembra/")
        .then(response => {
          const datos = Array.isArray(response.data) ? response.data : [response.data];
          this.siembras = datos.filter(s =>
            s.estado === 1 &&
            (typeof s.acuicola === "object"
              ? s.acuicola.id_acuicola === this.acuicolaId
              : s.acuicola === this.acuicolaId)
          );
        })
        .catch(error => console.error("Error al obtener siembras:", error));
    },
    obtenerEntradasUnitarias() {
      axios
        .get("/entrada-unitaria/")
        .then(response => {
          this.entradasUnitarias = Array.isArray(response.data)
            ? response.data
            : [response.data];
        })
        .catch(error => console.error("Error al obtener entradas unitarias:", error));
    },
    obtenerSalidasUnitarias() {
      axios
        .get("/salida-unitaria/")
        .then(response => {
          this.salidasUnitarias = Array.isArray(response.data)
            ? response.data
            : [response.data];
        })
        .catch(error => console.error("Error al obtener salidas unitarias:", error));
    },
    obtenerProductos() {
      axios
        .get("/producto/")
        .then(response => {
          this.productos = Array.isArray(response.data)
            ? response.data
            : [response.data];
        })
        .catch(error => console.error("Error al obtener productos:", error));
    },
    buscarProducto() {
      // Se actualiza automáticamente por el computed
    },
    seleccionarProducto(item) {
      console.log(">> seleccionarProducto, item:", item);
      if (item.disponible > 0) {
        // Almacenamos el id_entrada_unitaria y demás datos
        this.productoSeleccionado = {
          id_entrada_unitaria: item.id_entrada_unitaria,
          nombre: item.nombre,
          lote: item.lote,
          disponible: item.disponible,
          modo: item.modo
        };
        this.productoBusqueda = "";
      }
    },
    agregarProducto() {
      if (this.productoSeleccionado) {
        const existe = this.salida.productos.find(p =>
          p.id_entrada_unitaria === this.productoSeleccionado.id_entrada_unitaria &&
          p.lote === this.productoSeleccionado.lote
        );
        if (!existe) {
          this.salida.productos.push({
            id_entrada_unitaria: this.productoSeleccionado.id_entrada_unitaria,
            nombre: this.productoSeleccionado.nombre,
            lote: this.productoSeleccionado.lote,
            disponible: this.productoSeleccionado.disponible,
            modo: this.productoSeleccionado.modo,
            cantidad: 1
          });
        }
        this.productoSeleccionado = null;
      }
    },
    validarCantidad(index, cantidad) {
      const item = this.salida.productos[index];
      if (cantidad > item.disponible) {
        alert("La cantidad ingresada excede el stock disponible. Se ajustará al máximo permitido.");
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
    registrarSalida() {
      const salidaPayload = {
        solicitante: this.salida.solicitante,
        usuario: this.usuarioId,
        acuicola: this.acuicolaId,
        estado: 1
      };
      axios
        .post("/salida/", salidaPayload)
        .then(salidaRes => {
          const salidaId = salidaRes.data.id_salida_producto || salidaRes.data.id;
          if (!salidaId) {
            alert("No se recibió el ID de la salida. Verifique la respuesta del servidor.");
            return;
          }
          const destino = this.salida.area === "Estanque" ? "Estanque" : this.salida.area;
          const salidaUnitariaPromises = this.salida.productos.map(producto => {
            if (producto.cantidad > producto.disponible) {
              alert(`La cantidad para ${producto.nombre} excede el stock disponible. Corrige antes de continuar.`);
              throw new Error("Cantidad excede stock disponible.");
            }
            let cKg = 0;
            let cUnidades = 0;
            if (producto.modo === "kg") {
              cKg = producto.cantidad;
            } else {
              cUnidades = producto.cantidad;
            }
            const payloadUnitaria = {
              salida: salidaId,
              // Se envía el id de EntradaUnitaria en el campo "producto"
              producto: producto.id_entrada_unitaria,
              lote: producto.lote,
              cantidad: cUnidades,
              cantidad_kg: cKg,
              destino: destino,
              usuario: this.usuarioId,
              acuicola: this.acuicolaId,
              estado: 1
            };
            console.log("Enviando payload SalidaUnitaria:", payloadUnitaria);
            return axios.post("/salida-unitaria/", payloadUnitaria);
          });
          Promise.all(salidaUnitariaPromises)
            .then(respuestas => {
              if (this.salida.area === "Estanque" && this.siembraSeleccionada) {
                const siembraId = this.siembraSeleccionada;
                console.log("Siembra ID enviado:", siembraId);
                const salidaEstanquePromises = respuestas.map(resp => {
                  const salidaUnitariaId = resp.data.id_salida_unitaria || resp.data.id;
                  const payloadEstanque = {
                    salidaunitaria: salidaUnitariaId,
                    siembra: siembraId,
                    usuario: this.usuarioId,
                    acuicola: this.acuicolaId,
                    estado: 1
                  };
                  console.log("Enviando payload SalidaEstanque:", payloadEstanque);
                  return axios.post("/salida-estanque/", payloadEstanque);
                });
                return Promise.all(salidaEstanquePromises);
              }
            })
            .then(() => {
              alert("¡Salida registrada con éxito!");
              this.salida = { solicitante: "", area: "", productos: [] };
              this.siembraSeleccionada = null;
            })
            .catch(err => {
              console.error("Error al crear salidas unitarias o salida de estanque:", err);
            });
        })
        .catch(err => {
          console.error("Error al registrar la salida:", err);
          alert("Ocurrió un error al registrar la salida.");
        });
    }
  },
  mounted() {
    this.obtenerSiembras();
    this.obtenerEntradasUnitarias();
    this.obtenerSalidasUnitarias();
    this.obtenerProductos();
  }
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap");

.registro-salidas {
  font-family: "Poppins", sans-serif;
  max-width: auto;
  margin: 30px auto;
  padding: 30px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.registro-salidas h1 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #444;
  margin-bottom: 8px;
  font-size: 14px;
}

input,
select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: #f8f9fa;
  transition: border 0.3s ease;
}

input:focus,
select:focus {
  border-color: #28a745;
  outline: none;
}

.btn-agregar {
  background-color: #28a745;
  color: #fff;
  border: none;
  padding: 10px 15px;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 10px;
  transition: background 0.3s ease, transform 0.3s ease;
}

.btn-agregar:hover {
  background-color: #218838;
  transform: scale(1.02);
}

.btn-eliminar {
  background-color: #dc3545;
  color: #fff;
  border: none;
  padding: 6px 10px;
  font-size: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.btn-eliminar:hover {
  background-color: #c82333;
}

.btn-registrar {
  background-color: #007bff;
  color: #fff;
  border: none;
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 20px;
  transition: background 0.3s ease, transform 0.3s ease;
}

.btn-registrar:hover {
  background-color: #0069d9;
  transform: scale(1.02);
}

.autocomplete {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #ddd;
  border-radius: 0 0 8px 8px;
  background: #fff;
  max-height: 150px;
  overflow-y: auto;
}

.autocomplete li {
  padding: 10px;
  cursor: pointer;
  font-size: 14px;
}

.autocomplete li:hover {
  background-color: #f0f0f0;
}

.lista-productos {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.productos-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
  font-size: 14px;
}

.productos-table thead tr {
  background-color: #f5f5f5;
}

.productos-table th,
.productos-table td {
  text-align: center;
  padding: 12px 15px;
  border-bottom: 1px solid #eee;
}

.selected-product,
.selected-item {
  font-size: 14px;
  color: #333;
  margin-bottom: 10px;
}
</style>
