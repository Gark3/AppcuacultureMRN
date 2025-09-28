<template>
  <div class="registro-entradas">
    <h1>Registro de Entradas</h1>
    
    <!-- Buscador y selección de Proveedor -->
    <div class="form-group">
      <label for="proveedor">Buscar Proveedor</label>
      <input
        type="text"
        id="proveedor"
        v-model="buscadorProveedor"
        placeholder="Ingrese el nombre del proveedor..."
      />
      <ul v-if="proveedoresFiltrados.length" class="autocomplete">
        <li 
          v-for="proveedor in proveedoresFiltrados"
          :key="proveedor.id_proveedor"
          @click="seleccionarProveedor(proveedor)"
        >
          {{ proveedor.nombre }} - {{ proveedor.correo }}
        </li>
      </ul>
    </div>

    <!-- Proveedor seleccionado -->
    <div class="info-seleccion">
      <p>
        <strong>Proveedor seleccionado:</strong>
        <span v-if="proveedorSeleccionado">{{ proveedorSeleccionado.nombre }}</span>
        <span v-else>No seleccionado</span>
      </p>
    </div>

    <!-- Buscador y selección de Producto -->
    <div class="form-group">
      <label for="producto">Buscar Producto</label>
      <input
        type="text"
        id="producto"
        v-model="buscadorProducto"
        placeholder="Buscar producto por nombre..."
      />
      <ul v-if="productosFiltrados.length" class="autocomplete">
        <li 
          v-for="prod in productosFiltrados"
          :key="prod.id_producto"
          @click="seleccionarProducto(prod)"
        >
          {{ prod.nombre }}
        </li>
      </ul>
    </div>

    <!-- Información del producto seleccionado y formulario para agregar -->
    <div class="info-seleccion">
      <p>
        <strong>Producto seleccionado:</strong>
        <span v-if="productoSeleccionado">{{ productoSeleccionado.nombre }}</span>
        <span v-else>No seleccionado</span>
      </p>
      
      <div class="form-group switch-group">
        <label for="aplicaKg">¿Aplica KG?</label>
        <input type="checkbox" id="aplicaKg" v-model="aplicaKg" />
      </div>
      
      <div class="form-group" v-if="aplicaKg">
        <label for="kg">KG Totales</label>
        <input type="number" id="kg" v-model.number="kgTotales" min="0" required />
      </div>
      <div class="form-group" v-else>
        <label for="kg">KG Totales</label>
        <input type="number" id="kg" v-model.number="kgTotales" disabled />
      </div>
      
      <div class="form-group">
        <label for="cantidad">Cantidad (Unidades)</label>
        <input type="number" id="cantidad" v-model.number="cantidad" min="1" required />
      </div>
      
      <div class="form-group">
        <label for="costo">Costo por Unidad</label>
        <input type="number" id="costo" v-model.number="costo" min="0.01" step="0.01" required />
      </div>
      
      <!-- Campo para ingreso manual del lote -->
      <div class="form-group">
        <label for="lote">Lote del Producto</label>
        <input type="text" id="lote" v-model="lote" required />
      </div>
      
      <button type="button" @click="agregarProducto">Agregar Producto</button>
    </div>

    <!-- Lista de Productos Agregados (Tabla Profesional) -->
    <div v-if="listaProductos.length" class="lista-productos">
      <h2>Productos Agregados</h2>
      
      <table class="productos-table">
        <thead>
          <tr>
            <th>Producto</th>
            <th>Lote</th>
            <th>KG Totales</th>
            <th>Unidades</th>
            <th>Costo</th>
            <th>Total</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in listaProductos" :key="index">
            <td>{{ item.nombre }}</td>
            <td>{{ item.lote }}</td>
            <td>{{ item.kgTotales }}</td>
            <td>{{ item.cantidad }}</td>
            <td>{{ item.costo }}</td>
            <td>{{ item.total }}</td>
            <td>
              <button class="accion-btn" @click="editarProducto(index)">Editar</button>
              <button class="accion-btn" @click="eliminarProducto(index)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div class="costo-total">
        <strong>Costo Total:</strong> {{ costoTotal }}
      </div>
      <button class="recibir-btn" @click="recibirProductos" :disabled="listaProductos.length === 0">
        Recibir
      </button>
    </div>
    
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RegistroEntradas",
  data() {
    return {
      // Identificadores
      usuarioId: 1,     // Id del usuario que realiza la operación (campo "usuario" en BaseModel)
      acuicolaId: 1,    // Id de la acuícola (campo "acuicola" en BaseModel)
      
      buscadorProveedor: "",
      buscadorProducto: "",
      proveedores: [],
      productos: [],
      proveedorSeleccionado: null,
      productoSeleccionado: null,
      
      // Datos del producto a agregar
      aplicaKg: false,
      kgTotales: 0,
      cantidad: 1,
      costo: 0,
      lote: "",
      
      listaProductos: []
    };
  },
  computed: {
    proveedoresFiltrados() {
      let filtrados = this.proveedores.filter(p => {
        // Se comprueba que el proveedor pertenezca a la acuícola actual
        const acu = typeof p.acuicola === "object" ? p.acuicola.id_acuicola : p.acuicola;
        return acu === this.acuicolaId;
      });
      if (this.buscadorProveedor) {
        filtrados = filtrados.filter(p =>
          p.nombre.toLowerCase().includes(this.buscadorProveedor.toLowerCase())
        );
      }
      return filtrados.slice(0, 10);
    },
    productosFiltrados() {
      let filtrados = this.productos.filter(prod => {
        // Se comprueba que el producto pertenezca a la acuícola actual
        const acu = typeof prod.acuicola === "object" ? prod.acuicola.id_acuicola : prod.acuicola;
        return acu === this.acuicolaId;
      });
      if (this.buscadorProducto) {
        filtrados = filtrados.filter(prod =>
          prod.nombre.toLowerCase().includes(this.buscadorProducto.toLowerCase())
        );
      }
      return filtrados.slice(0, 10);
    },
    costoTotal() {
      return this.listaProductos
        .reduce((total, item) => total + item.total, 0)
        .toFixed(2);
    }
  },
  methods: {
    obtenerProveedores() {
      axios
        .get("/proveedor/")
        .then(response => {
          this.proveedores = Array.isArray(response.data)
            ? response.data
            : [response.data];
        })
        .catch(error => {
          console.error("Error al obtener proveedores:", error);
        });
    },
    obtenerProductos() {
      axios
        .get("/producto/")
        .then(response => {
          this.productos = Array.isArray(response.data)
            ? response.data
            : [response.data];
        })
        .catch(error => {
          console.error("Error al obtener productos:", error);
        });
    },
    seleccionarProveedor(proveedor) {
      this.proveedorSeleccionado = proveedor;
      this.buscadorProveedor = "";
    },
    seleccionarProducto(prod) {
      this.productoSeleccionado = prod;
      this.buscadorProducto = "";
      // Reinicia el campo de lote para ingreso manual
      this.lote = "";
    },
    agregarProducto() {
      if (this.cantidad > 0 && this.costo > 0 && this.lote) {
        // Calcula el total (cantidad * costo)
        const total = this.cantidad * this.costo;
        this.listaProductos.push({
          id: this.productoSeleccionado 
                ? this.productoSeleccionado.id_producto 
                : null,
          nombre: this.productoSeleccionado 
                ? this.productoSeleccionado.nombre 
                : "Producto sin selección",
          lote: this.lote,
          aplicaKg: this.aplicaKg,
          kgTotales: this.kgTotales,
          cantidad: this.cantidad,
          costo: this.costo,
          total: total
        });
        // Reinicia formulario de producto
        this.productoSeleccionado = null;
        this.aplicaKg = false;
        this.kgTotales = 0;
        this.cantidad = 1;
        this.costo = 0;
        this.lote = "";
      } else {
        alert("Complete correctamente los campos requeridos.");
      }
    },
    editarProducto(index) {
      const item = this.listaProductos[index];
      this.productoSeleccionado = {
        id_producto: item.id,
        nombre: item.nombre
      };
      this.aplicaKg = item.aplicaKg;
      this.kgTotales = item.kgTotales;
      this.cantidad = item.cantidad;
      this.costo = item.costo;
      this.lote = item.lote;
      this.listaProductos.splice(index, 1);
    },
    eliminarProducto(index) {
      this.listaProductos.splice(index, 1);
    },
    recibirProductos() {
      if (!this.proveedorSeleccionado) {
        alert("Por favor, seleccione un proveedor.");
        return;
      }

      // Se prepara el payload de la Entrada (tabla Entrada)
      // Nota: no es necesario enviar "fecha" ya que auto_now_add se encarga de ello.
      const entradaPayload = {
        provedor: this.proveedorSeleccionado.id_proveedor,
        usuario: this.usuarioId,      // Campo definido en BaseModel (usuario)
        acuicola: this.acuicolaId,      // Campo definido en BaseModel (acuicola)
        estado: 1                     // 1 = Activo, según lo definido en BaseModel
      };

      // Crea la Entrada principal
      axios
        .post("/entrada/", entradaPayload)
        .then(entradaRes => {
          // Se asume que la respuesta incluye el id de la entrada creada
          const entradaId = entradaRes.data.id_entrada_producto || entradaRes.data.id;
          if (!entradaId) {
            alert("No se recibió el ID de la entrada. Verifica la respuesta del servidor.");
            return;
          }

          // Por cada producto en la lista, crea una EntradaUnitaria
          const requests = this.listaProductos.map(item => {
            const payload = {
              entrada: entradaId,
              producto: item.id,
              cantidad_kg: item.aplicaKg ? item.kgTotales : 0,
              unidades: item.cantidad,
              costo: item.costo,
              lote: item.lote,
              
              // Campos del BaseModel
              usuario: this.usuarioId,
              acuicola: this.acuicolaId,
              estado: 1
            };

            return axios.post("/entrada-unitaria/", payload);
          });

          Promise.all(requests)
            .then(() => {
              alert("¡Productos recibidos con éxito!");
              // Reinicia la lista de productos y el proveedor seleccionado
              this.listaProductos = [];
              this.proveedorSeleccionado = null;
            })
            .catch(err => {
              console.error("Error al crear entradas unitarias:", err);
              alert("Ocurrió un error al registrar los productos en EntradaUnitaria.");
            });
        })
        .catch(err => {
          console.error("Error al crear la entrada:", err);
          alert("Ocurrió un error al crear la Entrada. Verifica los campos.");
        });
    }
  },
  mounted() {
    this.obtenerProveedores();
    this.obtenerProductos();
  }
};
</script>

<style scoped>
/* Tus estilos (manteniendo la estructura actual) */
.registro-entradas {
  font-family: 'Poppins', sans-serif;
  max-width: auto;
  margin: 30px auto;
  padding: 25px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

h1, h2 {
  text-align: center;
  color: #333;
}

/* Formularios e inputs */
.form-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
}

label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #444;
  font-size: 14px;
}

input,
select,
textarea {
  width: 100%;
  padding: 12px;
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: #f8f9fa;
}

/* Autocomplete */
.autocomplete {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #ddd;
  background: #fff;
  max-height: 150px;
  overflow-y: auto;
  border-radius: 0 0 8px 8px;
}

.autocomplete li {
  padding: 10px;
  cursor: pointer;
}

.autocomplete li:hover {
  background-color: #f0f0f0;
}

.info-seleccion p {
  font-size: 14px;
  margin: 5px 0 15px;
}

/* Tabla de Productos Agregados */
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

.productos-table th {
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #ddd;
}

.costo-total {
  margin-top: 15px;
  text-align: right;
  font-size: 16px;
  font-weight: 600;
  color: #444;
}

/* Botón Recibir */
.recibir-btn {
  margin-top: 20px;
  float: right;
  background-color: #28a745;
  color: #fff;
  border: none;
  padding: 12px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.recibir-btn:hover {
  background-color: #218838;
  transform: scale(1.02);
}

/* Botones generales */
button {
  background-color: #28a745;
  color: #fff;
  border: none;
  padding: 12px 15px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 600;
  text-transform: uppercase;
  width: 100%;
  margin-top: 20px;
}

button:hover {
  background-color: #218838;
  transform: scale(1.02);
}

/* Botones de acción pequeños para Editar y Eliminar */
.accion-btn {
  background: transparent;
  border: none;
  color: #555;
  font-size: 12px;
  padding: 2px 4px;
  margin: 0 2px;
  cursor: pointer;
}

.accion-btn:hover {
  color: #000;
  text-decoration: underline;
}
</style>
