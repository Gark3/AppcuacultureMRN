<template>
  <div class="inventario-fisico">
    <h1>Inventario Físico</h1>
    <form @submit.prevent="revisarInventario">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Descripción</th>
            <th>Cantidad Física</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="producto in productos" :key="producto.id">
            <td>{{ producto.id }}</td>
            <td>{{ producto.nombre }}</td>
            <td>{{ producto.descripcion }}</td>
            <td>
              <input type="number" v-model.number="producto.cantidadFisica" min="0" />
            </td>
          </tr>
        </tbody>
      </table>
      <button type="submit">Revisar</button>
    </form>

    <div v-if="mostrarModal" class="modal">
      <div class="modal-content">
        <h2>Revisión de Inventario</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Cantidad Física</th>
              <th>Cantidad Sistema</th>
              <th>Diferencia</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="producto in productos" :key="producto.id">
              <td>{{ producto.id }}</td>
              <td>{{ producto.nombre }}</td>
              <td>{{ producto.cantidadFisica }}</td>
              <td>{{ producto.cantidadSistema }}</td>
              <td>{{ producto.diferencia }}</td>
            </tr>
          </tbody>
        </table>
        <button @click="cerrarModal">Cerrar</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      productos: [
        { id: 1, nombre: 'Producto A', descripcion: 'Descripción A', cantidadSistema: 50, cantidadFisica: 0, diferencia: 0 },
        { id: 2, nombre: 'Producto B', descripcion: 'Descripción B', cantidadSistema: 30, cantidadFisica: 0, diferencia: 0 },
        { id: 3, nombre: 'Producto C', descripcion: 'Descripción C', cantidadSistema: 20, cantidadFisica: 0, diferencia: 0 }
      ],
      mostrarModal: false
    };
  },
  methods: {
    revisarInventario() {
      this.productos.forEach(producto => {
        producto.diferencia = producto.cantidadFisica - producto.cantidadSistema;
      });
      this.mostrarModal = true;
    },
    cerrarModal() {
      this.mostrarModal = false;
    }
  }
};
</script>

<style scoped>
.registro-siembra {
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

input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 5px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
/* Ajustar el cuadro de productos */
.product-table {
width: 100%; /* Ajustar al ancho del contenedor */
border-collapse: collapse;
}

.product-table th,
.product-table td {
padding: 10px;
text-align: center;
border: 1px solid #ccc;
}

.product-table th {
background-color: #f2f2f2;
}

.table-container {
overflow-x: auto; /* Hacer desplazable horizontalmente si es necesario */
max-width: 100%; /* Limitar al ancho del contenedor */
}
th, td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: center;
}

th {
  background-color: #f2f2f2;
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

/* Modal Styles */
.modal-overlay {
position: fixed;
top: 0;
left: 0;
width: 100%;
height: 100%;
background: rgba(0, 0, 0, 0.5);
display: flex;
justify-content: center;
align-items: center;
z-index: 1000;
}

.modal-content {
background: white;
padding: 20px;
border-radius: 10px;
max-width: auto;
width: 90%;
max-height: 80vh; /* Limitar la altura del modal */
overflow-y: auto; /* Hacer que el contenido sea desplazable */
box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-content h2 {
margin-top: 0;
}

.modal-content table {
width: 100%;
border-collapse: collapse;
}

.modal-content th,
.modal-content td {
border: 1px solid #ccc;
padding: 8px;
text-align: center;
}

.modal-content th {
background-color: #f2f2f2;
}

.modal-content button {
margin-top: 10px;
}
</style>
